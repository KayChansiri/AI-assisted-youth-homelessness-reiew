# Outputs

This folder is used for generated files created by the AI-assisted screening workflow.

Example output files may include:

- `ai_screening_results.csv`
- `alignment_results.csv`
- `evaluation_metrics.csv`

These generated files are not included in the public repository because they may contain licensed abstracts, project-specific screening decisions, or other restricted research data.

## Output file descriptions

### `ai_screening_results.csv`

This file contains the original abstract records plus AI-generated screening outputs.

For binary prompts, it includes:

- `Decision`
- `Explanation_Codes`
- `Focus_Area_Results` or `Eligibility_Results`

For Likert prompts, it includes:

- `Relevance_Score`
- `Focus_Area_Results` or `Eligibility_Results`

### `alignment_results.csv`

This file compares AI screening decisions with human screening decisions.

Possible alignment labels include:

- `Aligned: Both Include`
- `Aligned: Both Exclude`
- `AI Include, Human Exclude`
- `AI Exclude, Human Include`

### `evaluation_metrics.csv`

This file contains summary metrics:

- true positives
- false positives
- true negatives
- false negatives
- precision
- recall
- specificity
- accuracy
- F1 score
