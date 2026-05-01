import db
from scripts import seed_data
from flask import Flask, jsonify, render_template
import psycopg
import os
from psycopg.rows import dict_row


db.create_db()
db.create_table()
# seed_data.seed_data()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')


def get_conn():
    return psycopg.connect(
        dbname=os.environ.get('DB_NAME'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        host=os.environ.get('DB_HOST'),
        port=os.environ.get('DB_PORT')
    )


@app.route("/api/dashboard/summary")
def dashboard_summary():
    conn = get_conn()
    cur = conn.cursor(row_factory=dict_row)

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
        WHERE tr.id = (SELECT MAX(id) FROM test_runs)
        GROUP BY tr.id
    """)

    data = cur.fetchone()

    if data:
        total = data["total_tests"] or 0
        passed = data["passed"] or 0
        data["pass_rate"] = round((passed / total * 100), 2) if total else 0

    conn.close()
    return jsonify(data)


@app.route("/api/dashboard/trends")
def trends():
    conn = get_conn()
    cur = conn.cursor(row_factory=dict_row)

    cur.execute("""
        SELECT tr.run_date,
               COUNT(*) FILTER (WHERE tcr.status = 'passed') AS passed,
               COUNT(*) FILTER (WHERE tcr.status = 'failed') AS failed,
               ROUND(AVG(tcr.duration_seconds)::numeric, 2) AS avg_duration
        FROM test_runs tr
        JOIN test_case_results tcr ON tr.id = tcr.run_id
        GROUP BY tr.run_date
        ORDER BY tr.run_date
    """)

    data = cur.fetchall()
    conn.close()
    return jsonify(data)


@app.route("/api/dashboard/slow-tests")
def slow_tests():
    conn = get_conn()
    cur = conn.cursor(row_factory=dict_row)

    cur.execute("""
        SELECT test_name,
               ROUND(AVG(duration_seconds)::numeric, 2) AS avg_duration
        FROM test_case_results
        GROUP BY test_name
        ORDER BY avg_duration DESC
        LIMIT 10
    """)

    data = cur.fetchall()
    conn.close()
    return jsonify(data)


@app.route("/api/dashboard/flaky-tests")
def flaky_tests():
    conn = get_conn()
    cur = conn.cursor(row_factory=dict_row)

    cur.execute("""
        SELECT test_name,
               COUNT(*) FILTER (WHERE status = 'failed') AS failures,
               COUNT(*) AS total_runs,
               ROUND(
                   COUNT(*) FILTER (WHERE status = 'failed') * 100.0 / COUNT(*), 2
               ) AS failure_rate
        FROM test_case_results
        GROUP BY test_name
        HAVING COUNT(*) > 3
        ORDER BY failure_rate DESC
        LIMIT 10
    """)

    data = cur.fetchall()
    conn.close()
    return jsonify(data)


@app.route("/api/dashboard/area-breakdown")
def area_breakdown():
    conn = get_conn()
    cur = conn.cursor(row_factory=dict_row)

    cur.execute("""
        SELECT tc.area,
               COUNT(*) FILTER (WHERE tcr.status = 'passed') AS passed,
               COUNT(*) FILTER (WHERE tcr.status = 'failed') AS failed
        FROM test_case_results tcr
        JOIN test_cases tc ON tc.name = tcr.test_name
        GROUP BY tc.area
    """)

    data = cur.fetchall()
    conn.close()
    return jsonify(data)


@app.route("/api/dashboard/defects")
def defects():
    conn = get_conn()
    cur = conn.cursor(row_factory=dict_row)

    cur.execute("""
        SELECT severity, COUNT(*) AS count
        FROM defects
        GROUP BY severity
    """)

    data = cur.fetchall()
    conn.close()
    return jsonify(data)


@app.route("/api/insights")
def insights():
    conn = get_conn()
    cur = conn.cursor(row_factory=dict_row)

    from services.insights import generate_insights

    cur.execute("SELECT area, COUNT(*) FROM defects GROUP BY area")
    defects = [{"area": r[0], "count": r[1]} for r in cur.fetchall()]

    cur.execute("""
        SELECT tc.area,
               SUM(CASE WHEN tr.status='failed' THEN 1 ELSE 0 END) * 1.0 / COUNT(*)
        FROM test_case_results tr
        JOIN test_cases tc ON tr.test_name = tc.name
        GROUP BY tc.area
    """)
    fail_rates = [{"area": r[0], "fail_rate": float(r[1])} for r in cur.fetchall()]

    data = generate_insights(defects, fail_rates, [])

    return jsonify(data)


@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    # app.run(debug=app.config.get("DEBUG", False), port=5002)
    app.run(host="0.0.0.0", port=5002, debug=app.config.get("DEBUG", False))
