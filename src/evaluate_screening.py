"""
Evaluate AI-assisted abstract screening against human reviewer decisions.

This script:
1. Loads AI screening results.
2. Loads human screening decisions.
3. Merges them by study ID.
4. Converts binary or Likert AI outputs into include/exclude decisions.
5. Calculates precision, recall, specificity, accuracy, and F1 score.
"""

import argparse
from pathlib import Path
from typing import Any, Dict

import pandas as pd
import yaml


def load_config(config_path: str) -> Dict[str, Any]:
    """Load settings from a YAML configuration file."""
    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def load_table(file_path: str) -> pd.DataFrame:
    """Load a CSV or Excel file."""
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".csv":
        return pd.read_csv(path)

    if suffix in [".xlsx", ".xls"]:
        return pd.read_excel(path)

    raise ValueError("File must be a .csv, .xlsx, or .xls file.")


def save_table(df: pd.DataFrame, file_path: str) -> None:
    """Save a DataFrame as CSV or Excel."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    suffix = path.suffix.lower()

    if suffix == ".csv":
        df.to_csv(path, index=False)
    elif suffix in [".xlsx", ".xls"]:
        df.to_excel(path, index=False)
    else:
        raise ValueError("Output file must be a .csv, .xlsx, or .xls file.")


def convert_ai_output_to_binary(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
    """
    Convert AI output into ai_include.

    Binary prompts:
    - Decision = Include becomes 1
    - Decision = Exclude becomes 0

    Likert prompts:
    - Relevance_Score greater than or equal to threshold becomes 1
    - Relevance_Score below threshold becomes 0
    """
    df = df.copy()
    prompt_type = config["prompt_type"]

    if "likert" in prompt_type:
        threshold = config.get("likert_include_threshold", 3)

        if "Relevance_Score" not in df.columns:
            raise ValueError("Likert prompt selected, but Relevance_Score column is missing.")

        df["Relevance_Score"] = pd.to_numeric(df["Relevance_Score"], errors="coerce")
        df["ai_include"] = (df["Relevance_Score"] >= threshold).astype(int)

    else:
        if "Decision" not in df.columns:
            raise ValueError("Binary prompt selected, but Decision column is missing.")

        df["ai_include"] = (
            df["Decision"]
            .astype(str)
            .str.strip()
            .str.lower()
            .eq("include")
            .astype(int)
        )

    return df


def create_alignment_label(row: pd.Series, human_col: str) -> str:
    """Create a plain-language alignment label."""
    ai_include = row["ai_include"]
    human_include = row[human_col]

    if ai_include == 1 and human_include == 1:
        return "Aligned: Both Include"

    if ai_include == 0 and human_include == 0:
        return "Aligned: Both Exclude"

    if ai_include == 1 and human_include == 0:
        return "AI Include, Human Exclude"

    if ai_include == 0 and human_include == 1:
        return "AI Exclude, Human Include"

    return "Other"


def calculate_metrics(df: pd.DataFrame, human_col: str) -> Dict[str, float]:
    """Calculate confusion matrix counts and evaluation metrics."""
    ai = df["ai_include"].astype(int)
    human = df[human_col].astype(int)

    tp = int(((ai == 1) & (human == 1)).sum())
    fp = int(((ai == 1) & (human == 0)).sum())
    tn = int(((ai == 0) & (human == 0)).sum())
    fn = int(((ai == 0) & (human == 1)).sum())

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    accuracy = (tp + tn) / (tp + fp + tn + fn) if (tp + fp + tn + fn) > 0 else 0
    f1_score = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0
    )

    return {
        "true_positives": tp,
        "false_positives": fp,
        "true_negatives": tn,
        "false_negatives": fn,
        "precision": precision,
        "recall": recall,
        "specificity": specificity,
        "accuracy": accuracy,
        "f1_score": f1_score,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to configuration YAML file.",
    )
    args = parser.parse_args()

    config = load_config(args.config)

    study_id_col = config["study_id_column"]
    human_col = config["human_decision_column"]

    ai_df = load_table(config["output_file"])
    human_df = load_table(config["human_file"])

    ai_df = convert_ai_output_to_binary(ai_df, config)

    if study_id_col not in ai_df.columns:
        raise ValueError(f"Study ID column '{study_id_col}' not found in AI file.")

    if study_id_col not in human_df.columns:
        raise ValueError(f"Study ID column '{study_id_col}' not found in human file.")

    if human_col not in human_df.columns:
        raise ValueError(f"Human decision column '{human_col}' not found in human file.")

    merged = ai_df.merge(
        human_df[[study_id_col, human_col]],
        on=study_id_col,
        how="inner",
    )

    merged[human_col] = pd.to_numeric(merged[human_col], errors="coerce").astype(int)
    merged["Alignment"] = merged.apply(
        lambda row: create_alignment_label(row, human_col),
        axis=1,
    )

    metrics = calculate_metrics(merged, human_col)

    alignment_output = "outputs/alignment_results.csv"
    metrics_output = "outputs/evaluation_metrics.csv"

    save_table(merged, alignment_output)
    pd.DataFrame([metrics]).to_csv(metrics_output, index=False)

    print("\nConfusion Matrix Counts")
    print(f"True Positives: {metrics['true_positives']}")
    print(f"False Positives: {metrics['false_positives']}")
    print(f"True Negatives: {metrics['true_negatives']}")
    print(f"False Negatives: {metrics['false_negatives']}")

    print("\nAI Screening Metrics")
    print(f"Precision: {metrics['precision']:.3f}")
    print(f"Recall: {metrics['recall']:.3f}")
    print(f"Specificity: {metrics['specificity']:.3f}")
    print(f"Accuracy: {metrics['accuracy']:.3f}")
    print(f"F1 Score: {metrics['f1_score']:.3f}")

    print(f"\nAlignment file saved to: {alignment_output}")
    print(f"Metrics file saved to: {metrics_output}")


if __name__ == "__main__":
    main()
