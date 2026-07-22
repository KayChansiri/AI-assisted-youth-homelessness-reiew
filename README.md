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
