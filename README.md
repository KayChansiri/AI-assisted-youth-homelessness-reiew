## Prompt Structure

This repository includes six prompt files.

The prompts are organized by two dimensions:

1. **Screening strategy**
2. **Decision format**

---

## Screening Strategies

### Prompt 1: Strict Eligibility Screening

This prompt asks the model to apply eligibility criteria conservatively.

The model includes a study only when the title, abstract, and metadata strongly suggest that all eligibility criteria are met.

This strategy is useful for showing why strict final-decision logic may be too conservative during title and abstract screening. In early screening, abstracts often do not contain enough information to confirm every eligibility criterion.

Prompt files:

- `prompts/prompt_1_strict_binary.txt`
- `prompts/prompt_1_strict_likert.txt`

---

### Prompt 2: Screening Assistant / Triage

This prompt asks the model to act as an early screening assistant.

The goal is to identify studies that may be relevant enough for human full-text review. The model is instructed not to make a final eligibility decision at the abstract stage.

This strategy better matches the purpose of title and abstract screening, where ambiguous but potentially relevant records are often retained for human review.

Prompt files:

- `prompts/prompt_2_triage_binary.txt`
- `prompts/prompt_2_triage_likert.txt`

---

### Prompt 3: Expanded Inclusion Logic

This prompt asks the model to use a broader interpretation of relevance.

It allows studies to be flagged when they plausibly intersect with youth homelessness populations, services, systems, or risk pathways. This includes studies involving mixed-age samples, housing-related interventions, systems-level services, public health interventions, foster care transitions, education services, or homelessness-adjacent contexts.

This strategy was designed to reduce missed studies during abstract screening.

Prompt files:

- `prompts/prompt_3_expanded_binary.txt`
- `prompts/prompt_3_expanded_likert.txt`

---

## Decision Formats

Each screening strategy is available in two formats.

### Binary Format

The model returns a direct screening decision:

- `Include`
- `Exclude`

Binary outputs are easier to compare directly with human screening decisions.

Example output:

```json
{
  "Decision": "Include",
  "Explanation_Codes": [],
  "Focus_Area_Results": {
    "Original_Empirical": "Yes",
    "Youth_Age_13_25": "Yes",
    "Homelessness_Target": "Yes",
    "Program_Focus": "Yes"
  }
}
```

---

### Likert Format

The model returns a relevance score:

- `1` = very unlikely to be relevant
- `2` = unlikely to be relevant
- `3` = possibly relevant
- `4` = likely relevant
- `5` = very likely relevant

Likert outputs allow the model to express uncertainty. For evaluation, scores at or above the selected threshold are converted to `Include`.

Example output:

```json
{
  "Relevance_Score": 4,
  "Focus_Area_Results": {
    "Original_Empirical": "Yes",
    "Youth_Age_13_25": "Yes",
    "Homelessness_Target": "Yes",
    "Program_Focus": "Yes"
  }
}
```

---

## Available Prompt Types

The configuration file can use one of the following prompt types:

```text
prompt_1_strict_binary
prompt_1_strict_likert
prompt_2_triage_binary
prompt_2_triage_likert
prompt_3_expanded_binary
prompt_3_expanded_likert
```

Example:

```yaml
prompt_type: "prompt_3_expanded_binary"
```

---

## Data Templates

The repository includes example data templates only.

### Abstract Input File

The abstract input file should include one row per study record.

Recommended columns:

- `study_id`
- `title`
- `abstract`
- `publication_year`
- `journal_name`
- `publisher`
- `author`
- `author_affiliation`
- `keywords`

Template file:

```text
data_templates/abstract_input_template.csv
```

---

### Human Screening File

The human screening file should include:

- `study_id`
- `human_include`

where:

- `1` = included by human reviewers
- `0` = excluded by human reviewers

Template file:

```text
data_templates/human_screening_template.csv
```

---

## Data Sharing Note

The full abstract datasets used in the project are not included in this public repository.

Database records and abstracts may be subject to licensing, copyright, or project-specific restrictions. This repository provides code templates, prompt templates, and workflow documentation so other teams can adapt the approach using their own data.

Do not upload private, licensed, or confidential review data to a public repository.

---

## Setup

Install the required Python packages:

```bash
pip install -r requirements.txt
```

---

## API Key Note

Do not paste your OpenAI API key directly into the code.

Set your API key as an environment variable before running the workflow.

On Mac or Linux:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

On Windows PowerShell:

```powershell
setx OPENAI_API_KEY "your-api-key-here"
```

The `.gitignore` file is set up so that private configuration files and generated outputs are not accidentally uploaded.

---

## Configuration

Copy the example configuration file:

```bash
cp config.example.yaml config.yaml
```

Then edit `config.yaml`.

Example configuration:

```yaml
model: "gpt-5-mini"
input_file: "data_templates/abstract_input_template.csv"
human_file: "data_templates/human_screening_template.csv"
output_file: "outputs/ai_screening_results.csv"

prompt_type: "prompt_3_expanded_binary"

study_id_column: "study_id"
human_decision_column: "human_include"

likert_include_threshold: 3
sleep_seconds: 0.5
```

---

## Running AI Screening

To run AI-assisted abstract screening:

```bash
python src/run_screening.py --config config.yaml
```

This creates an AI screening output file, such as:

```text
outputs/ai_screening_results.csv
```

For binary prompts, the output will include fields such as:

- `Decision`
- `Explanation_Codes`
- `Focus_Area_Results`

For Likert prompts, the output will include fields such as:

- `Relevance_Score`
- `Focus_Area_Results`

---

## Evaluating AI Screening

To compare AI screening decisions with human screening decisions:

```bash
python src/evaluate_screening.py --config config.yaml
```

The evaluation script creates files such as:

```text
outputs/alignment_results.csv
outputs/evaluation_metrics.csv
```

---

## Evaluation Metrics

The workflow calculates:

- **True positives:** AI included a study that humans also included.
- **False positives:** AI included a study that humans excluded.
- **True negatives:** AI excluded a study that humans also excluded.
- **False negatives:** AI excluded a study that humans included.
- **Precision:** Of studies AI included, how many humans also included.
- **Recall:** Of studies humans included, how many AI successfully caught.
- **Specificity:** Of studies humans excluded, how many AI correctly excluded.
- **Accuracy:** Overall share of AI decisions that matched human decisions.
- **F1 score:** A combined measure of precision and recall.

For early title and abstract screening, recall is especially important because missed studies may never move forward to full-text review.

---

## Optional: List Available Models

To list available OpenAI models for your account:

```bash
python src/list_models.py
```

This is optional. Model availability may vary by account and over time.

---

## How to Adapt This Workflow

Other review teams can adapt this workflow by:

1. Preparing their own abstract file.
2. Preparing their own human screening file.
3. Editing the prompt files to match their review question.
4. Choosing a model and prompt type in `config.yaml`.
5. Running AI screening.
6. Comparing AI decisions with human decisions.
7. Selecting the prompt and model setup that best fits their review goal.

The results from one review topic may not transfer directly to another. Each team should test and validate the workflow in its own evidence context.

---

## Important Limitations

This workflow should be interpreted with caution.

- AI screening outputs may vary by model, prompt, and review topic.
- A prompt that performs well for youth homelessness intervention evidence may not perform the same way for another field.
- High recall may increase the number of irrelevant studies sent to human reviewers.
- High specificity may reduce human workload but increase the risk of missing relevant studies.
- Model names, availability, cost, and behavior may change over time.
- Human validation remains necessary.

---

## Recommended Use

This repository is best used as a transparent workflow template for AI-assisted screening.

It is intended for:

- researchers;
- policy analysts;
- evidence synthesis teams;
- students;
- service-system researchers;
- community-partnered research teams.

It is not intended to automate final systematic review decisions.

---

## Citation

If you use or adapt this workflow, please cite the project website or associated publication when available.

---

## Contact

For questions about this project, please refer to the project website (https://livingyouthevidence.org/) or contact the project PI at kchansiri@chapinhall.org
