"""
Phase 6: Operational Layer

Consumes the corrected Phase 1-5 outputs and produces a
state dashboard, executive summary, and machine-readable JSON.
"""

import json
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"


def load_outputs():
    required = [
        "01_analytical_dataset.csv",
        "03_model_predictions.csv",
        "04_model_metrics.csv",
        "05_feature_importance.csv",
        "06_state_segments.csv",
        "07_segment_summaries.csv",
        "08_state_rankings.csv",
    ]

    missing = [f for f in required if not (OUT / f).exists()]
    if missing:
        raise FileNotFoundError(
            "Missing required outputs:\n"
            + "\n".join(f" - {f}" for f in missing)
            + "\nRun main.py and phase_5_prescriptive.py first."
        )

    return {
        "analytics": pd.read_csv(OUT / "01_analytical_dataset.csv"),
        "predictions": pd.read_csv(OUT / "03_model_predictions.csv"),
        "metrics": pd.read_csv(OUT / "04_model_metrics.csv"),
        "importance": pd.read_csv(OUT / "05_feature_importance.csv"),
        "segments": pd.read_csv(OUT / "06_state_segments.csv"),
        "summaries": pd.read_csv(OUT / "07_segment_summaries.csv"),
        "rankings": pd.read_csv(OUT / "08_state_rankings.csv"),
    }


def create_dashboard(data):
    analytics = data["analytics"]
    predictions = data["predictions"]
    segments = data["segments"]
    rankings = data["rankings"]

    prediction_year = int(predictions["Year_Num"].max())

    latest = analytics[
        analytics["Year_Num"] == prediction_year
    ][["State", "LFPR", "WPR", "UR"]].drop_duplicates("State")

    pred = predictions[
        predictions["Year_Num"] == prediction_year
    ].copy()

    dashboard = pred.merge(latest, on="State", how="left")

    dashboard = dashboard.merge(
        segments[["State", "Cohort", "Focus_Areas"]],
        on="State",
        how="left",
    )

    dashboard = dashboard.merge(
        rankings[["State", "State_Rank"]],
        on="State",
        how="left",
    )

    previous = analytics[
        analytics["Year_Num"] == prediction_year - 1
    ][["State", "LFPR"]].rename(
        columns={"LFPR": "Previous_LFPR"}
    )

    dashboard = dashboard.merge(previous, on="State", how="left")

    dashboard["LFPR_Change"] = (
        dashboard["LFPR"] - dashboard["Previous_LFPR"]
    ).round(2)

    dashboard["Predicted_Improving_Next_Year"] = (
        dashboard["RandomForest_Prediction"]
        .map({1: "Yes", 0: "No"})
    )

    dashboard["Prediction_Probability_Pct"] = (
        dashboard["RandomForest_Probability"] * 100
    ).round(1)

    return dashboard[
        [
            "State_Rank",
            "State",
            "Cohort",
            "LFPR",
            "WPR",
            "UR",
            "LFPR_Change",
            "Predicted_Improving_Next_Year",
            "Prediction_Probability_Pct",
            "Focus_Areas",
        ]
    ].sort_values("State_Rank")


def create_summary(data, dashboard):
    analytics = data["analytics"]
    metrics = data["metrics"]
    importance = data["importance"]
    summaries = data["summaries"]

    latest_year = int(analytics["Year_Num"].max())
    first_year = int(analytics["Year_Num"].min())

    latest_lfpr = analytics[
        analytics["Year_Num"] == latest_year
    ]["LFPR"].mean()

    first_lfpr = analytics[
        analytics["Year_Num"] == first_year
    ]["LFPR"].mean()

    improving = int(
        (dashboard["Predicted_Improving_Next_Year"] == "Yes").sum()
    )

    rf = metrics[metrics["Model"] == "RandomForest"]

    if not rf.empty:
        row = rf.iloc[0]
        performance = (
            f"Accuracy={row['Accuracy']:.3f}, "
            f"Precision={row['Precision']:.3f}, "
            f"Recall={row['Recall']:.3f}, "
            f"F1={row['F1']:.3f}, "
            f"ROC-AUC={row['AUC_ROC']:.3f}"
        )
    else:
        performance = "Random Forest metrics unavailable."

    top_features = "\n".join(
        f"   - {r['Feature']}: {r['Importance']:.3f}"
        for _, r in importance.head(5).iterrows()
    )

    return f"""
WOMEN'S ECONOMIC EMPOWERMENT ML PIPELINE
PHASE 6: EXECUTIVE SUMMARY
Generated: {datetime.now(tz=datetime.now().astimezone().tzinfo).strftime("%Y-%m-%d %H:%M:%S %Z")}

PURPOSE
Classify whether female LFPR is likely to improve by at least
5 percentage points in the following year and group states into
analytical cohorts.

DATA
States: {analytics["State"].nunique()}
Analytical period: {first_year}-{latest_year}
Prediction target year: {latest_year + 1}

LFPR OVERVIEW
Average female LFPR in {first_year}: {first_lfpr:.2f}%
Average female LFPR in {latest_year}: {latest_lfpr:.2f}%
Change: {latest_lfpr - first_lfpr:+.2f} percentage points.

MODEL PERFORMANCE
Random Forest: {performance}

Predicted to improve in {latest_year + 1}:
{improving} of {len(dashboard)} states.

COHORT SUMMARY
{summaries.to_string(index=False)}

TOP RANDOM FOREST FEATURES
{top_features}

INTERPRETATION
The model identifies historical predictive associations. It does not
establish that any feature causes female LFPR to increase.

LIMITATIONS
- The time-based test set contains 36 state-year observations.
- Education and vocational-training measures are national-level.
- PMMY growth is treated as a national temporal feature.
- The 2026 Udyam snapshot is excluded from historical prediction features.
- Childcare, social norms, safety, household decisions, wages,
  migration and other important factors are not fully represented.

RECOMMENDED USE
Use state rankings and cohorts to support further investigation.
Combine the model with qualitative research, local expertise and
causal evaluation before making policy decisions.
""".strip()


def create_json(data, dashboard):
    analytics = data["analytics"]

    return {
        "metadata": {
            "project_name": "Women's Economic Empowerment ML Pipeline",
            "phase": 6,
            "generated": datetime.now(tz=datetime.now().astimezone().tzinfo).isoformat(),
            "latest_feature_year": int(analytics["Year_Num"].max()),
            "target_year": int(analytics["Year_Num"].max()) + 1,
        },
        "data_summary": {
            "states": int(analytics["State"].nunique()),
            "first_year": int(analytics["Year_Num"].min()),
            "latest_year": int(analytics["Year_Num"].max()),
        },
        "model_metrics": data["metrics"].round(4).to_dict(
            orient="records"
        ),
        "feature_importance": data["importance"].round(4).to_dict(
            orient="records"
        ),
        "cohort_summary": data["summaries"].to_dict(
            orient="records"
        ),
        "state_dashboard": dashboard.to_dict(
            orient="records"
        ),
    }


def run_phase_6():
    print("\n" + "=" * 55)
    print("PHASE 6: OPERATIONAL LAYER")
    print("=" * 55)

    data = load_outputs()

    print("1. Creating state dashboard...")
    dashboard = create_dashboard(data)
    dashboard.to_csv(
        OUT / "10_state_dashboard_2023.csv",
        index=False,
    )
    print(f"   ✓ {len(dashboard)} states")

    print("2. Creating executive summary...")
    (OUT / "11_executive_summary.txt").write_text(
        create_summary(data, dashboard),
        encoding="utf-8",
    )
    print("   ✓ Executive summary created")

    print("3. Creating project JSON...")
    (OUT / "12_project_summary.json").write_text(
        json.dumps(
            create_json(data, dashboard),
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )
    print("   ✓ Project JSON created")

    completion = f"""PHASE 6 COMPLETE
Generated: {datetime.now(tz=datetime.now().astimezone().tzinfo).strftime("%Y-%m-%d %H:%M:%S %Z")}
Latest feature year: {int(data["analytics"]["Year_Num"].max())}
Prediction target year: {int(data["analytics"]["Year_Num"].max()) + 1}
States: {len(dashboard)}

Outputs:
- 10_state_dashboard_2023.csv
- 11_executive_summary.txt
- 12_project_summary.json
- 13_phase_6_complete.txt
"""

    (OUT / "13_phase_6_complete.txt").write_text(
        completion,
        encoding="utf-8",
    )

    print("4. Phase 6 complete.")
    print("   ✓ 10_state_dashboard_2023.csv")
    print("   ✓ 11_executive_summary.txt")
    print("   ✓ 12_project_summary.json")
    print("   ✓ 13_phase_6_complete.txt")

    return dashboard


if __name__ == "__main__":
    run_phase_6()
