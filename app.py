import os
import psycopg
from psycopg.rows import dict_row
from flask import Flask, jsonify, render_template

import db

# -------------------------
# INIT DB (dev convenience)
# -------------------------
db.create_db()
db.create_table()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")


# -------------------------
# DB CONNECTION
# -------------------------
def get_conn():
    return psycopg.connect(
        dbname=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        host=os.environ.get("DB_HOST"),
        port=os.environ.get("DB_PORT"),
        row_factory=dict_row
    )


# =========================================================
# UI
# =========================================================
@app.route("/")
def home():
    return render_template("index.html")


# =========================================================
# FILTER DATA (BUILD + RUNS)
# =========================================================

@app.route("/api/dashboard/builds")
def get_builds():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT DISTINCT build_version
        FROM test_runs
        ORDER BY build_version DESC
    """)

    builds = [row["build_version"] for row in cur.fetchall()]
    conn.close()

    return jsonify(builds)


@app.route("/api/dashboard/runs/<build_version>")
def get_runs(build_version):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, run_date, run_scope, build_version
        FROM test_runs
        WHERE build_version = %s
        ORDER BY run_date DESC
    """, (build_version,))

    runs = cur.fetchall()
    conn.close()

    return jsonify(runs)


# =========================================================
# SUMMARY (PER RUN)
# =========================================================
@app.route("/api/dashboard/summary/<int:run_id>")
def dashboard_summary(run_id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT tr.id AS run_id,
               tr.run_date,
               tr.build_version,
               tr.run_scope,
               tr.total_tests,
               COUNT(tcr.*) FILTER (WHERE tcr.status = 'passed') AS passed,
               COUNT(tcr.*) FILTER (WHERE tcr.status = 'failed') AS failed,
               ROUND(AVG(tcr.duration_seconds)::numeric, 2) AS avg_duration
        FROM test_runs tr
        LEFT JOIN test_case_results tcr ON tr.id = tcr.run_id
        WHERE tr.id = %s
        GROUP BY tr.id
    """, (run_id,))

    data = cur.fetchone()

    if data:
        total = data["total_tests"] or 0
        passed = data["passed"] or 0

        data["pass_rate"] = round((passed / total * 100), 2) if total else 0

    conn.close()
    return jsonify(data)


# =========================================================
# TRENDS (OPTIONALLY FILTERED BY BUILD)
# =========================================================
@app.route("/api/dashboard/trends/<build_version>")
def trends(build_version):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT tr.id AS run_id,
               tr.run_date,
               tr.build_version,
               COUNT(*) FILTER (WHERE tcr.status = 'passed') AS passed,
               COUNT(*) FILTER (WHERE tcr.status = 'failed') AS failed,
               ROUND(AVG(tcr.duration_seconds)::numeric, 2) AS avg_duration
        FROM test_runs tr
        JOIN test_case_results tcr ON tr.id = tcr.run_id
        WHERE tr.build_version = %s
        GROUP BY tr.id, tr.run_date, tr.build_version
        ORDER BY tr.run_date
    """, (build_version,))

    data = cur.fetchall()
    print(build_version)
    print(data)
    conn.close()

    return jsonify(data)


# =========================================================
# AREA BREAKDOWN (PER RUN)
# =========================================================
@app.route("/api/dashboard/area-breakdown/<int:run_id>")
def area_breakdown(run_id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT tc.area,
               COUNT(*) FILTER (WHERE tcr.status = 'passed') AS passed,
               COUNT(*) FILTER (WHERE tcr.status = 'failed') AS failed
        FROM test_case_results tcr
        JOIN test_cases tc ON tc.name = tcr.test_name
        WHERE tcr.run_id = %s
        GROUP BY tc.area
        ORDER BY failed DESC
    """, (run_id,))

    data = cur.fetchall()
    conn.close()

    return jsonify(data)


# =========================================================
# SLOW TESTS (PER RUN)
# =========================================================
@app.route("/api/dashboard/slow-tests/<int:run_id>")
def slow_tests(run_id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT test_name,
               ROUND(AVG(duration_seconds)::numeric, 2) AS avg_duration
        FROM test_case_results
        WHERE run_id = %s
        GROUP BY test_name
        ORDER BY avg_duration DESC
        LIMIT 10
    """, (run_id,))

    data = cur.fetchall()
    conn.close()

    return jsonify(data)


# =========================================================
# FLAKY TESTS (PER RUN)
# =========================================================
@app.route("/api/dashboard/flaky-tests/<int:run_id>")
def flaky_tests(run_id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT test_name,
               COUNT(*) FILTER (WHERE status = 'failed') AS failures,
               COUNT(*) AS total_runs,
               ROUND(
                   COUNT(*) FILTER (WHERE status = 'failed') * 100.0 / COUNT(*), 2
               ) AS failure_rate
        FROM test_case_results
        WHERE run_id = %s
        GROUP BY test_name
        HAVING COUNT(*) > 3
        ORDER BY failure_rate DESC
        LIMIT 10
    """, (run_id,))

    data = cur.fetchall()
    conn.close()

    return jsonify(data)


# =========================================================
# INSIGHTS (OPTIONAL - STILL WORKS)
# =========================================================
@app.route("/api/insights/<int:run_id>")
def insights(run_id):
    from services.insights import generate_insights

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT tc.area, COUNT(*) AS count
        FROM defects d
        JOIN test_cases tc ON tc.name = d.test_name
        WHERE d.run_id = %s
        GROUP BY tc.area
    """, (run_id,))
    defects = [{"area": r["area"], "count": r["count"]} for r in cur.fetchall()]

    cur.execute("""
        SELECT tc.area,
               SUM(CASE WHEN tcr.status='failed' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS fail_rate
        FROM test_case_results tcr
        JOIN test_cases tc ON tc.name = tcr.test_name
        WHERE tcr.run_id = %s
        GROUP BY tc.area
    """, (run_id,))
    fail_rates = [
        {"area": r["area"], "fail_rate": float(r["fail_rate"] or 0)}
        for r in cur.fetchall()
    ]

    conn.close()

    return jsonify(generate_insights(defects, fail_rates, []))


# -------------------------
# RUN APP
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
