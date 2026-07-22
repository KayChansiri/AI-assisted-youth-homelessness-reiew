# AI-Assisted Youth Homelessness Review

This repository contains code and documentation for an AI-assisted abstract screening workflow developed for a living systematic review of youth homelessness interventions.

The workflow uses large language models to support title and abstract screening. It is designed as a human-in-the-loop screening aid, not as a replacement for human reviewers.

## What the workflow does

The workflow:

1. Loads a spreadsheet or CSV file of study abstracts.
2. Applies a screening prompt to each abstract using an OpenAI model.
3. Saves AI-generated screening decisions.
4. Merges AI decisions with human screening decisions.
5. Calculates performance metrics such as recall, precision, specificity, accuracy, and F1 score.

## Why this workflow was developed

Systematic reviews are time-consuming to update. This project explores whether AI-assisted screening can help review teams identify potentially relevant studies more efficiently while preserving human validation and final decision-making.

## Important caution

AI screening results should not be treated as final inclusion decisions. Review teams should validate AI outputs against human screening decisions before using the workflow in practice.

## Repository structure

- `src/`: reusable Python scripts
- `prompts/`: prompt templates and prompt notes
- `data_templates/`: example input file structures
- `notebooks/`: optional notebooks for step-by-step use
- `outputs/`: generated AI screening and evaluation files

## Setup

Install the required packages:

```bash
pip install -r requirements.txt

## Prompt structure

This repository includes six prompt files.

The prompts are organized by two dimensions:

1. Screening strategy
2. Decision format

### Screening strategies

#### Prompt 1: Strict eligibility screening

This prompt asks the model to apply eligibility criteria conservatively. It includes a study only when the abstract and metadata strongly suggest that all criteria are met.

This prompt is useful for showing why strict final-decision logic may be too conservative during title and abstract screening.

#### Prompt 2: Screening assistant / triage

This prompt asks the model to act as an early screening assistant. The goal is to identify studies that may be relevant enough for human full-text review.

This prompt better matches the purpose of title and abstract screening.

#### Prompt 3: Expanded inclusion logic

This prompt asks the model to use a broader interpretation of relevance. It includes mixed-age samples, housing-related interventions, systems-level services, and homelessness-adjacent contexts when they may plausibly relate to youth homelessness intervention evidence.

This prompt was designed to reduce missed studies during abstract screening.

### Decision formats

Each screening strategy is available in two formats:

#### Binary format

The model returns:

- `Include`
- `Exclude`

Binary outputs are easier to compare directly with human screening decisions.

#### Likert format

The model returns a relevance score:

- 1 = very unlikely to be relevant
- 2 = unlikely to be relevant
- 3 = possibly relevant
- 4 = likely relevant
- 5 = very likely relevant

Likert outputs allow the model to express uncertainty. For evaluation, scores at or above the selected threshold are converted to Include.

## Available prompt files

- `prompts/prompt_1_strict_binary.txt`
- `prompts/prompt_1_strict_likert.txt`
- `prompts/prompt_2_triage_binary.txt`
- `prompts/prompt_2_triage_likert.txt`
- `prompts/prompt_3_expanded_binary.txt`
- `prompts/prompt_3_expanded_likert.txt`
