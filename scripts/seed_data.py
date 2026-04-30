import random
from datetime import date, timedelta
from app import get_conn as conn


def seed_data():


    areas = ["Login", "Payments", "Pricing", "Trade Booking"]

    # # Insert test cases
    # for i in range(50):
    #     conn.cursor.execute("""
    #         INSERT INTO test_cases (name, type, area)
    #         VALUES (%s, %s, %s)
    #     """, (
    #         f"Test Case {i}",
    #         random.choice(["manual", "automated"]),
    #         random.choice(areas)
    #     ))
    #
    # # Insert test runs
    # for i in range(30):
    #     run_date = date.today() - timedelta(days=i)
    #     exec_time = random.randint(300, 2000)
    #
    #     conn.cursor.execute("""
    #         INSERT INTO test_runs (run_date, execution_time_seconds, build_version)
    #         VALUES (%s, %s, %s)
    #     """, (run_date, exec_time, f"v{i}"))
    #
    #
    # conn.cursor.execute("""
    #        INSERT
    #        INTO
    #        defects(created_date, severity, area, test_case_id)
    #        VALUES
    #        ('2024-01-01', 'High', 'Payments', 1),
    #        ('2024-01-02', 'Medium', 'Payments', 2),
    #        ('2024-01-03', 'Low', 'Login', 3),
    #        ('2024-01-04', 'High', 'Login', 4),
    #        ('2024-01-05', 'Low', 'Login', 5),
    #        ('2024-01-06', 'Medium', 'Trading', 6),
    #        ('2024-01-07', 'High', 'Trading', 7),
    #        ('2024-01-08', 'Low', 'Trading', 8);
    #         """)

    conn().cursor().execute("""
            INSERT
            INTO
            test_results (test_case_id, run_id, status, execution_time)
            VALUES
            (51, 35, 'pass', 120),
            (53, 35, 'fail', 140),
            (55, 35, 'fail', 200),
            (57, 35, 'pass', 110),
            (59, 35, 'fail', 300),
            (60, 35, 'pass', 100),
            (61, 35, 'pass', 90),
            (65, 35, 'fail', 250),
            (69, 35, 'pass', 130),
            (75, 35, 'pass', 150);
             """)

    conn().commit()
    conn().close()
