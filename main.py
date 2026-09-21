"""
Women's Economic Empowerment ML Pipeline
Phases 1-4: EDA, data integration, feature engineering, model training.

This version is designed for the supplied NDAP/PLFS CSV files.
It predicts whether female LFPR will improve by >=5 percentage
points in the following year, avoiding same-year target leakage.
"""

import warnings
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

FILES = {
    2: RAW / "2.csv",
    3: RAW / "3.csv",
    4: RAW / "4.csv",
    10: RAW / "10.csv",
    13: RAW / "13.csv",
    16: RAW / "16.csv",
}


def extract_year(series):
    return pd.to_numeric(
        series.astype(str).str.extract(r"(\d{4})$")[0],
        errors="coerce",
    )


def load_plfs():
    df = pd.read_csv(FILES[3])
    df = df[df["Gender"].eq("Female")].copy()

    value_cols = {
        "Labour Force Participation Rate According To Usual Status (Ps+Ss) (UOM:%(Percentage)), Scaling Factor:1": "LFPR",
        "Worker Population Rate According To Usual Status (Ps+Ss) (UOM:%(Percentage)), Scaling Factor:1": "WPR",
        " Unemployment Rate According To Usual Status (Ps+Ss) (UOM:%(Percentage)), Scaling Factor:1": "UR",
    }

    df["Year_Num"] = extract_year(df["Year"])
    df = df.rename(columns=value_cols)

    return (
        df.groupby(["State", "Year_Num"], as_index=False)[["LFPR", "WPR", "UR"]]
        .mean()
    )


def add_target(base):
    df = base.sort_values(["State", "Year_Num"]).copy()

    # Target is the CHANGE IN THE NEXT YEAR.
    # This prevents the current year's change from directly revealing the target.
    next_lfpr = df.groupby("State")["LFPR"].shift(-1)
    df["Next_LFPR_Change"] = next_lfpr - df["LFPR"]
    df["Target_Improved"] = (df["Next_LFPR_Change"] >= 5).astype(int)

    # Historical change, available at prediction time.
    df["LFPR_YoY_Change"] = df.groupby("State")["LFPR"].diff()

    return df


def process_industry():
    df = pd.read_csv(FILES[10])
    df = df[df["Gender"].eq("Female")].copy()
    df["Year_Num"] = extract_year(df["Year"])

    agriculture = next(
        c for c in df.columns
        if "Agriculture, Forestry And Fishing" in c
    )
    mining = next(
        c for c in df.columns
        if "Mining And Quarrying" in c
    )

    df["NonAgriculture_Pct"] = (
        100
        - pd.to_numeric(df[agriculture], errors="coerce").fillna(0)
        - pd.to_numeric(df[mining], errors="coerce").fillna(0)
    ).clip(0, 100)

    return (
        df.groupby(["State", "Year_Num"], as_index=False)["NonAgriculture_Pct"]
        .mean()
    )


def process_education():
    df = pd.read_csv(FILES[13])
    df = df[df["Gender"].eq("Female")].copy()
    df["Year_Num"] = extract_year(df["Year"])

    col = next(
        c for c in df.columns
        if "Persons With Secondary Level And Above Education" in c
    )

    df[col] = pd.to_numeric(df[col], errors="coerce")

    return (
        df.groupby("Year_Num", as_index=False)[col]
        .mean()
        .rename(columns={col: "SecondaryPlus_Pct"})
    )


def process_vocational():
    df = pd.read_csv(FILES[4])
    df = df[
        (df["Gender"] == "Female")
        & (df["Type Of Residence"] == "Rural+Urban")
        & (
            df["Type Of Technical Training"]
            == "Vocational/Technical Training Received_Formal & Other than Formal"
        )
    ].copy()

    df["Year_Num"] = extract_year(df["Year"])

    pct_col = next(
        c for c in df.columns
        if "Percentage Distribution" in c
    )

    df[pct_col] = pd.to_numeric(df[pct_col], errors="coerce")

    return (
        df.groupby("Year_Num", as_index=False)[pct_col]
        .mean()
        .rename(columns={pct_col: "VocationalTraining_Pct"})
    )


def process_pmmy():
    df = pd.read_csv(FILES[2])
    df["Year_Num"] = extract_year(df["Year"])

    account_col = next(
        c for c in df.columns
        if "Number Of Loan Account" in c
    )

    df[account_col] = pd.to_numeric(df[account_col], errors="coerce")
    df = df.sort_values("Year_Num")

    # National PMMY loan-account growth.
    df["PMMY_Growth"] = df[account_col].pct_change() * 100

    return df[["Year_Num", "PMMY_Growth"]].dropna(subset=["Year_Num"])


def build_dataset():
    base = add_target(load_plfs())

    industry = process_industry()
    education = process_education()
    vocational = process_vocational()
    pmmy = process_pmmy()

    df = (
        base
        .merge(industry, on=["State", "Year_Num"], how="left")
        .merge(education, on="Year_Num", how="left")
        .merge(vocational, on="Year_Num", how="left")
        .merge(pmmy, on="Year_Num", how="left")
    )

    df = df.sort_values(["State", "Year_Num"])

    # Historical state-level LFPR trajectory.
    df["LFPR_Lag1"] = df.groupby("State")["LFPR"].shift(1)
    df["LFPR_Lag2"] = df.groupby("State")["LFPR"].shift(2)

    # No Urban_Pct_Proxy:
    # WPR/LFPR is not a valid measure of urbanisation.

    # 2023 cannot be used because there is no 2024 LFPR target.
    df = df[df["Next_LFPR_Change"].notna()].copy()

    return df.reset_index(drop=True)


def save_eda_outputs(df):
    df.to_csv(OUT / "01_analytical_dataset.csv", index=False)

    summary = pd.DataFrame(
        {
            "metric": [
                "rows",
                "states",
                "years",
                "missing_cells",
                "improved_targets",
                "stagnant_targets",
            ],
            "value": [
                len(df),
                df["State"].nunique(),
                f"{int(df['Year_Num'].min())}-{int(df['Year_Num'].max())}",
                int(df.isna().sum().sum()),
                int(df["Target_Improved"].sum()),
                int((df["Target_Improved"] == 0).sum()),
            ],
        }
    )

    summary.to_csv(OUT / "EDA_summary.csv", index=False)

    trend = df.groupby("Year_Num")["LFPR"].mean()

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(trend.index, trend.values, marker="o")
    ax.set_title("Average Female LFPR by Year")
    ax.set_xlabel("Year")
    ax.set_ylabel("LFPR (%)")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "02_LFPR_trend.png", dpi=200)
    plt.close(fig)


def train_models(df):
    features = [
        "LFPR",
        "WPR",
        "UR",
        "SecondaryPlus_Pct",
        "VocationalTraining_Pct",
        "NonAgriculture_Pct",
        "PMMY_Growth",
        "LFPR_Lag1",
        "LFPR_Lag2",
    ]

    # Time-based split.
    train = df[df["Year_Num"] <= 2021].copy()
    test = df[df["Year_Num"] == 2022].copy()

    X_train = train[features]
    y_train = train["Target_Improved"]
    X_test = test[features]
    y_test = test["Target_Improved"]

    numeric_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    preprocess = ColumnTransformer(
        [("numeric", numeric_pipeline, features)]
    )

    models = {
        "LogisticRegression": LogisticRegression(
            class_weight="balanced",
            max_iter=2000,
            random_state=42,
        ),
        "RandomForest": RandomForestClassifier(
            n_estimators=300,
            max_depth=8,
            min_samples_split=5,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        ),
    }

    metrics = []
    predictions = test[
        ["State", "Year_Num", "Target_Improved", "Next_LFPR_Change"]
    ].copy()

    for name, model in models.items():
        pipeline = Pipeline(
            [
                ("preprocess", preprocess),
                ("model", model),
            ]
        )

        pipeline.fit(X_train, y_train)

        pred = pipeline.predict(X_test)
        prob = pipeline.predict_proba(X_test)[:, 1]

        auc = roc_auc_score(y_test, prob)

        metrics.append(
            {
                "Model": name,
                "Accuracy": accuracy_score(y_test, pred),
                "Precision": precision_score(
                    y_test, pred, zero_division=0
                ),
                "Recall": recall_score(
                    y_test, pred, zero_division=0
                ),
                "F1": f1_score(y_test, pred, zero_division=0),
                "AUC_ROC": auc,
            }
        )

        predictions[f"{name}_Prediction"] = pred
        predictions[f"{name}_Probability"] = prob

        joblib.dump(
            pipeline,
            OUT / f"{name}.joblib",
        )

        if name == "RandomForest":
            importances = pd.DataFrame(
                {
                    "Feature": features,
                    "Importance": pipeline.named_steps[
                        "model"
                    ].feature_importances_,
                }
            ).sort_values("Importance", ascending=False)

            importances.to_csv(
                OUT / "05_feature_importance.csv",
                index=False,
            )

    pd.DataFrame(metrics).to_csv(
        OUT / "04_model_metrics.csv",
        index=False,
    )

    predictions.to_csv(
        OUT / "03_model_predictions.csv",
        index=False,
    )

    print("\nMODEL RESULTS")
    print(pd.DataFrame(metrics).round(3).to_string(index=False))

    print("\nRandom Forest classification report:")
    print(
        classification_report(
            y_test,
            predictions["RandomForest_Prediction"],
            zero_division=0,
        )
    )


def main():
    print("\nWomen's Economic Empowerment Pipeline")
    print("=" * 45)

    missing = [
        str(path)
        for path in FILES.values()
        if not path.exists()
    ]

    if missing:
        print("\nMissing raw files:")
        for path in missing:
            print(" -", path)

        print(
            "\nPlace 2.csv, 3.csv, 4.csv, 10.csv, "
            "13.csv and 16.csv inside data/raw/"
        )
        return False

    print("\n[1/4] Loading and building analytical dataset...")
    df = build_dataset()

    print(
        f"Created {len(df)} rows for "
        f"{df['State'].nunique()} states."
    )

    print("[2/4] Saving EDA outputs...")
    save_eda_outputs(df)

    print("[3/4] Training models...")
    train_models(df)

    print("\n[4/4] Complete.")
    print(f"Outputs saved to: {OUT}")

    return True


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
