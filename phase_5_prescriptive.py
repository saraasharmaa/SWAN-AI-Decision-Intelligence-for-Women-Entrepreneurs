"""
Phase 5: State Segmentation and Policy Context

Consumes:
    outputs/01_analytical_dataset.csv
    outputs/03_model_predictions.csv

Produces:
    outputs/06_state_segments.csv
    outputs/07_segment_summaries.csv
    outputs/08_state_rankings.csv
    outputs/09_caveats_and_limitations.txt
"""

from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"


def load_inputs():
    analytics_path = OUT / "01_analytical_dataset.csv"
    predictions_path = OUT / "03_model_predictions.csv"

    if not analytics_path.exists():
        raise FileNotFoundError(
            "01_analytical_dataset.csv not found. Run 'python main.py' first."
        )
    if not predictions_path.exists():
        raise FileNotFoundError(
            "03_model_predictions.csv not found. Run 'python main.py' first."
        )

    return pd.read_csv(analytics_path), pd.read_csv(predictions_path)


def segment_states(analytics, predictions):
    latest_year = predictions["Year_Num"].max()

    latest_predictions = predictions[
        predictions["Year_Num"] == latest_year
    ].copy()

    current = analytics[
        analytics["Year_Num"] == latest_year
    ][["State", "LFPR", "WPR", "UR"]].drop_duplicates("State")

    df = latest_predictions.merge(current, on="State", how="left")

    median_lfpr = df["LFPR"].median()

    def assign_cohort(row):
        improving = row["RandomForest_Prediction"] == 1

        if improving and row["LFPR"] < median_lfpr:
            return "Growing but Constrained"
        if not improving and row["LFPR"] < median_lfpr:
            return "Low Participation"
        if improving and row["LFPR"] >= median_lfpr:
            return "High Potential"
        return "At Risk"

    df["Cohort"] = df.apply(assign_cohort, axis=1)
    df["Prediction_Year"] = latest_year
    df["LFPR_Median"] = median_lfpr

    return df


def get_intervention_context():
    return {
        "Low Participation": (
            "Investigate participation barriers; strengthen foundational "
            "skills and access to suitable employment opportunities."
        ),
        "At Risk": (
            "Investigate weakening momentum and examine sectoral and "
            "employment-quality changes."
        ),
        "Growing but Constrained": (
            "Identify factors associated with positive momentum and examine "
            "skills, access and employment opportunities."
        ),
        "High Potential": (
            "Sustain positive momentum while examining employment quality, "
            "retention and advancement."
        ),
    }


def create_summary(segments):
    rows = []

    cohort_order = [
        "Low Participation",
        "At Risk",
        "Growing but Constrained",
        "High Potential",
    ]

    for cohort in cohort_order:
        group = segments[segments["Cohort"] == cohort]
        if group.empty:
            continue

        rows.append({
            "Cohort": cohort,
            "Num_States": len(group),
            "Pct_States": round(100 * len(group) / len(segments), 1),
            "Avg_LFPR": round(group["LFPR"].mean(), 2),
            "Avg_WPR": round(group["WPR"].mean(), 2),
            "Avg_UR": round(group["UR"].mean(), 2),
            "Pct_Predicted_Improving": round(
                100 * group["RandomForest_Prediction"].mean(), 1
            ),
        })

    return pd.DataFrame(rows)


def create_rankings(segments):
    priority = {
        "Low Participation": 1,
        "At Risk": 2,
        "Growing but Constrained": 3,
        "High Potential": 4,
    }

    df = segments.copy()
    df["Cohort_Priority"] = df["Cohort"].map(priority)

    df = df.sort_values(
        ["Cohort_Priority", "LFPR"],
        ascending=[True, True],
    ).reset_index(drop=True)

    df["State_Rank"] = range(1, len(df) + 1)

    return df[[
        "State_Rank",
        "State",
        "Cohort",
        "LFPR",
        "WPR",
        "UR",
        "RandomForest_Prediction",
        "RandomForest_Probability",
        "Next_LFPR_Change",
    ]]


def create_caveats():
    return f"""
WOMEN'S ECONOMIC EMPOWERMENT ML PIPELINE
PHASE 5: CAVEATS AND LIMITATIONS
Generated: {datetime.now(tz=datetime.now().astimezone().tzinfo).strftime("%Y-%m-%d %H:%M:%S %Z")}

1. CORRELATION, NOT CAUSATION
The model identifies historical associations with next-year female LFPR
improvement. Predictions and feature importance do not establish causation.

2. PREDICTION TARGET
The target is whether female LFPR increases by at least 5 percentage
points in the following year. This is a classification problem, not a
long-term LFPR forecast.

3. TEMPORAL VALIDATION
The current pipeline trains through 2021 and tests on 2022 observations.
The test set contains 36 state-year observations.

4. DATA LIMITATIONS
Important factors such as childcare, social norms, safety, household
decisions, wages, migration and employment quality are not fully
represented in the supplied datasets.

5. NATIONAL-LEVEL FEATURES
Education and vocational-training measures used here are national-level
measures broadcast across states. PMMY growth is also treated as a
national temporal feature. They are not state-specific measurements.

6. UDYAM DATA
The 2026 Udyam snapshot is excluded from historical prediction features
because using future information would create data leakage.

7. MODEL PERFORMANCE
Use outputs/04_model_metrics.csv for the actual performance of the
corrected model. The small time-based test set requires cautious
interpretation of metrics.

8. POLICY USE
Cohorts are analytical groupings for investigation and prioritisation.
They are not automatic policy prescriptions. Causal evaluation,
qualitative research and domain expertise are required before
implementing interventions.
""".strip()


def run_phase_5():
    print("\n" + "=" * 55)
    print("PHASE 5: STATE SEGMENTATION")
    print("=" * 55)

    analytics, predictions = load_inputs()
    segments = segment_states(analytics, predictions)
    summaries = create_summary(segments)
    rankings = create_rankings(segments)

    context = get_intervention_context()
    segments["Focus_Areas"] = segments["Cohort"].map(context)

    segments.to_csv(OUT / "06_state_segments.csv", index=False)
    summaries.to_csv(OUT / "07_segment_summaries.csv", index=False)
    rankings.to_csv(OUT / "08_state_rankings.csv", index=False)
    (OUT / "09_caveats_and_limitations.txt").write_text(
        create_caveats(), encoding="utf-8"
    )

    print(f"Prediction year: {int(segments['Prediction_Year'].iloc[0])}")
    print(f"States segmented: {len(segments)}")
    print("\nCohort counts:")
    print(segments["Cohort"].value_counts().to_string())

    print("\nCreated:")
    print("  ✓ 06_state_segments.csv")
    print("  ✓ 07_segment_summaries.csv")
    print("  ✓ 08_state_rankings.csv")
    print("  ✓ 09_caveats_and_limitations.txt")

    return segments, summaries, rankings


if __name__ == "__main__":
    run_phase_5()
