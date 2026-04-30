QA Intelligence Dashboard

A lightweight test analytics platform built on top of pytest, PostgreSQL, and Flask.
It captures test execution data in real time and exposes meaningful insights through a clean dashboard.

Overview

This project started as a way to go beyond pass/fail reporting and answer more useful questions:

Are tests getting slower over time?
Which areas of the system are most unstable?
Which tests are flaky?
How does each run compare to previous runs?

The result is a simple but extensible system that combines test execution tracking with a web-based dashboard.

Tech Stack
Python / pytest – test execution and hooks
PostgreSQL – data storage
Flask – API layer
Vanilla JS + Chart.js + Tailwind – dashboard UI
psycopg (v3) – database connectivity
Architecture
pytest → hooks → PostgreSQL → Flask API → Dashboard UI
Key flow:
pytest executes tests
hooks capture:
run metadata (build version, scope)
test results (status, duration)
data is stored in PostgreSQL
Flask APIs aggregate and expose metrics
frontend renders charts and tables
Database Schema
test_runs

Stores each execution run

run_date
build_version
run_scope
total_tests
test_cases

Master list of test definitions

name (unique pytest nodeid)
type (manual / automated)
area (api, ui, etc.)
test_case_results

Execution results per run

run_id
test_name
duration_seconds
status (passed / failed)
defects (planned)
severity
area
test_case_id
Features
Run Tracking
captures build version and scope via CLI
tracks execution time and total tests
Test Result Analytics
pass / fail counts
pass rate calculation
average duration
Dashboard Metrics
trend over time (pass/fail)
slowest tests
flaky tests (failure rate)
breakdown by area (API, UI, etc.)
Extensible Design
easy to add new metrics
supports CI/CD integration
can evolve into a full test intelligence platform
Getting Started
1. Install dependencies
pip install -r requirements.txt
2. Set environment variables
export DB_NAME=your_db
export DB_USER=your_user
export DB_PASSWORD=your_password
export DB_HOST=localhost
export DB_PORT=5432
3. Run tests with tracking
pytest qa/tests \
  --build-version=1.1 \
  --scope=regression \
  --log-cli-level=INFO
4. Start the Flask app
python app.py
5. Open dashboard
http://localhost:5000
Example Insights
Identify slow tests impacting execution time
Detect flaky tests with high failure rates
Track regression trends across builds
Compare performance between runs
Design Notes
Uses pytest hooks (pytest_sessionstart, pytest_runtest_makereport) to capture data
Stores test identity using pytest nodeid
Separates test definitions (test_cases) from execution results
Uses PostgreSQL aggregation for efficient analytics
Future Enhancements
Defect tracking integration (Jira/Xray style)
Run comparison (current vs previous)
Coverage tracking (executed vs defined tests)
Performance regression alerts
Authentication / multi-user support
CI/CD pipeline integration
Why This Project

Most test frameworks stop at reporting results.
This project focuses on making test data useful — turning execution output into actionable insights.

Author

Built as part of a personal QA engineering portfolio focused on:

test automation architecture
data-driven testing
observability in QA systems