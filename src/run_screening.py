"""
Run AI-assisted abstract screening.

This script:
1. Loads a CSV or Excel file of study abstracts.
2. Loads one prompt file from the prompts/ folder.
3. Sends each abstract to an OpenAI model.
4. Saves AI screening decisions to an output file.

Human reviewers remain responsible for validation and final inclusion decisions.
"""

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any, Dict

import pandas as pd
import yaml
from openai import OpenAI


PROMPT_FILES = {
    "prompt_1_strict_binary": "prompts/prompt_1_strict_binary.txt",
    "prompt_1_strict_likert": "prompts/prompt_1_strict_likert.txt",
    "prompt_2_triage_binary": "prompts/prompt_2_triage_binary.txt",
    "prompt_2_triage_likert": "prompts/prompt_2_triage_likert.txt",
    "prompt_3_expanded_binary": "prompts/prompt_3_expanded_binary.txt",
    "prompt_3_expanded_likert": "prompts/prompt_3_expanded_likert.txt",
}


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

    raise ValueError("Input file must be a .csv, .xlsx, or .xls file.")


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


def load_prompt(prompt_type: str) -> str:
    """Load the prompt text that matches the selected prompt type."""
    if prompt_type not in PROMPT_FILES:
        valid_types = ", ".join(PROMPT_FILES.keys())
        raise ValueError(
            f"Unknown prompt_type: {prompt_type}. Valid options are: {valid_types}"
        )

    prompt_path = Path(PROMPT_FILES[prompt_type])

    with open(prompt_path, "r", encoding="utf-8") as file:
        return file.read()


def make_study_details(row: pd.Series) -> str:
    """
    Convert one study row into a text block inserted into the prompt.

    The prompt files should contain this placeholder:
    {study_details}
    """
    return f"""
Title: {row.get("title", "")}
Abstract: {row.get("abstract", "")}
Publication Year: {row.get("publication_year", "")}
Journal Name: {row.get("journal_name", "")}
Publisher: {row.get("publisher", "")}
Author: {row.get("author", "")}
Author Affiliation: {row.get("author_affiliation", "")}
Keywords: {row.get("keywords", "")}
""".strip()


def build_prompt(prompt_template: str, row: pd.Series) -> str:
    """Insert study details into the selected prompt template."""
    study_details = make_study_details(row)
    return prompt_template.replace("{study_details}", study_details)


def clean_json_response(text: str) -> str:
    """Remove markdown code fences if the model returns them."""
    text = text.strip()

    if text.startswith("```json"):
        text = text.replace("```json", "", 1).strip()
        text = text.rstrip("`").strip()

    elif text.startswith("```"):
        text = text.replace("```", "", 1).strip()
        text = text.rstrip("`").strip()

    return text


def call_openai_model(client: OpenAI, model: str, prompt: str) -> Dict[str, Any]:
    """Send one prompt to the OpenAI model and parse the JSON response."""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are an expert reviewer assisting with systematic review abstract screening.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    reply = response.choices[0].message.content
    cleaned_reply = clean_json_response(reply)

    return json.loads(cleaned_reply)


def screen_row(
    client: OpenAI,
    model: str,
    prompt_template: str,
    row: pd.Series,
    row_number: int,
) -> Dict[str, Any]:
    """Screen one abstract and return a structured result."""
    prompt = build_prompt(prompt_template, row)

    try:
        result = call_openai_model(client, model, prompt)
        return result

    except json.JSONDecodeError as error:
        print(f"JSON parse error on row {row_number}: {error}")
        return {
            "Decision": None,
            "Relevance_Score": None,
            "Explanation_Codes": ["JSON parse error"],
            "Focus_Area_Results": {},
            "Raw_Error": str(error),
        }

    except Exception as error:
        print(f"API or processing error on row {row_number}: {error}")
        return {
            "Decision": None,
            "Relevance_Score": None,
            "Explanation_Codes": ["API or processing error"],
            "Focus_Area_Results": {},
            "Raw_Error": str(error),
        }


def run_screening(config: Dict[str, Any]) -> pd.DataFrame:
    """Run AI screening for all rows in the input file."""
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise EnvironmentError(
            "OPENAI_API_KEY is not set. Do not paste your API key into the code. "
            "Set it as an environment variable before running this script."
        )

    client = OpenAI(api_key=api_key)

    model = config["model"]
    prompt_type = config["prompt_type"]
    prompt_template = load_prompt(prompt_type)

    df = load_table(config["input_file"])

    results = []

    for index, row in df.iterrows():
        row_number = index + 1
        result = screen_row(
            client=client,
            model=model,
            prompt_template=prompt_template,
            row=row,
            row_number=row_number,
        )

        results.append(result)

        time.sleep(config.get("sleep_seconds", 0.5))

    results_df = pd.DataFrame(results)

    output_df = pd.concat([df.reset_index(drop=True), results_df], axis=1)

    # Store complex columns as JSON strings so they save cleanly.
    for column in ["Explanation_Codes", "Focus_Area_Results", "Eligibility_Results"]:
        if column in output_df.columns:
            output_df[column] = output_df[column].apply(
                lambda value: json.dumps(value) if isinstance(value, (list, dict)) else value
            )

    return output_df


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to configuration YAML file.",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    output_df = run_screening(config)

    save_table(output_df, config["output_file"])

    print(f"Screening complete. File saved to: {config['output_file']}")


if __name__ == "__main__":
    main()
