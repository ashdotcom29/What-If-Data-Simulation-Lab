# WHAT IF? — Interactive Data Simulation & Comparison Lab

A Python desktop application for experimenting with CSV datasets, comparing hypothetical scenarios, and reviewing statistical changes.

## Features
- Upload any reasonably structured CSV dataset.
- Preview rows and inspect numerical summaries.
- Run percentage, add, subtract, multiply, conditional, filter and remove-row experiments.
- Preserve the original dataset while creating named scenarios.
- Compare a scenario or a second CSV against the original.
- View comparison charts and automatically generated descriptive insights.
- Export modified datasets and text reports.
- Save a lightweight experiment history in JSON.

## Requirements
- Python 3.9 or newer
- Tkinter (usually included with standard Python installations)
- Packages listed in `requirements.txt`

## Setup (Windows / VS Code)

Open the project folder in VS Code, then open Terminal and run:

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

If `python` does not work, try `py` in its place.

## Quick start
1. Click **Load sample dataset** in Dataset Explorer, or upload your own `.csv`.
2. Open **Experiment Lab**.
3. Enter a scenario name, choose a numeric target column and operation.
4. Optionally select a condition column and enter a condition.
5. Click **Run experiment**.
6. Open **Comparison Studio**, choose the scenario and click **Compare now**.
7. Generate insights and export a report from **Insights & Reports**.

## Notes
- Experiments always start from the original dataset; they do not overwrite it.
- Arithmetic operations are available for numerical columns only.
- Filter and remove operations use the condition controls.
- For a second-dataset comparison, matching column names and numeric data types are required for numeric mean comparisons.
- The generated observations describe the data changes; they do not establish real-world causation or predict outcomes.
- Experiment history stores scenario names and descriptions, not the full dataset contents.

## Project structure

```text
WhatIf_Data_Simulation_Lab/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── run.bat
├── experiment_history.json   (created automatically)
└── data/
    └── sample_student_data.csv
```
