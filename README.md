# EduGrant — Scholarship Eligibility Screening System

A deterministic scholarship screener built with Python's standard library. The system uses lists and dictionaries for application records, explains each rule-based decision, and provides both a browser dashboard and a console menu.

## Features

- Add and validate applications, including category and previous scholarship status.
- Screen applicants against academic, attendance, income, backlog, and enrollment rules.
- Classify applicants as **Highly Eligible**, **Eligible**, **Conditionally Eligible**, or **Not Eligible**.
- Show rule-by-rule explanations and a 0–100 merit score.
- Search and filter the registry, view summary counts, and rank eligible applicants.
- Delete a student by ID from the console or dashboard, with confirmation.
- Download a consolidated report with generation date and time.
- Includes an optional menu-driven console version.

Category and previous scholarship status are recorded and shown in explanations and reports. The assignment does not define eligibility effects for these fields, so they do not change the result.

## Requirements

- Python 3.8 or newer
- No third-party Python packages

## Run the web dashboard

From the project directory:

```text
python app.py
```

Open <http://127.0.0.1:8000/> in your browser. Stop the server with `Ctrl+C`.

To use a different local port:

```text
python app.py --port 8001
```

## Run the console menu

```text
python app.py --cli
```

The menu supports displaying applications, screening and searching records, filtering and ranking eligible students, summaries, timestamps, report generation, and confirmed deletion by student ID.

## Screening rules

Mandatory conditions are CGPA **at least 7.00**, attendance **at least 75%**, family income **no more than Rs. 5,00,000**, no more than **1 backlog**, and **Active** enrollment. Highly Eligible additionally requires CGPA **at least 8.50** and attendance **at least 85%**. Conditional eligibility applies only when CGPA is from **6.75 up to (but not including) 7.00** and all the other mandatory conditions pass.

The merit score preserves the existing weighting: CGPA contributes 60% and attendance contributes 40%.

## Simple project layout

```text
app.py                     Menu and program entry point
data.py                    Sample applications (list of dictionaries)
screening.py               Validation, rules, scores, explanations, report
web.py                     Standard-library local web server
templates/
  index.html               Dashboard markup
static/
  css/style.css            Responsive dashboard styles
  js/main.js               Browser-side registry interactions
```

Applications are held in memory as required by the assignment; records added in a session are cleared when the program stops.

