import os
from pathlib import Path
import psycopg
from dotenv import load_dotenv

file_path = Path(__file__).parent / "test.env"
load_dotenv(file_path)


def create_db():
    try:
        # Connect to the default database (e.g. 'postgres')
        with psycopg.connect(
                host=os.environ.get('DB_HOST'),
                dbname=os.environ.get('DB_NAME_DEFAULT'),
                user=os.environ.get('DB_USER'),
                password=os.environ.get('DB_PASSWORD'),
                port=os.environ.get('DB_PORT')
        ) as conn:
            # Enable autocommit mode
            conn.autocommit = True

            with conn.cursor() as cur:
                db_name = os.environ.get('DB_NAME')
                cur.execute(f"CREATE DATABASE {db_name};")
                print("Database created successfully!")

    except psycopg.Error as e:
        print(f"Duplicate DB: {e}")


def create_table():
    # Connect to your target database
    with psycopg.connect(
            dbname=os.environ.get('DB_NAME'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASSWORD'),
            host=os.environ.get('DB_HOST'),
            port=os.environ.get('DB_PORT')
    ) as conn:
        conn.autocommit = True  # Apply changes immediately (no explicit commit needed)

        with conn.cursor() as cur:

            cur.execute("""
                CREATE TABLE IF NOT EXISTS test_runs (
                id SERIAL PRIMARY KEY,
                run_date DATE,
                build_version TEXT,
                run_scope TEXT,
                total_tests INT
                );
                """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS test_cases (
                id SERIAL PRIMARY KEY,
                name TEXT,
                type TEXT, -- manual / automated
                area TEXT
                );
                """)

            try:
                cur.execute("""
                    ALTER TABLE test_cases
                    ADD CONSTRAINT unique_test_case_name UNIQUE (name);
                """)
            except Exception:
                pass

            cur.execute("""
                CREATE TABLE IF NOT EXISTS test_case_results (
                id SERIAL PRIMARY KEY,
                run_id INT REFERENCES test_runs(id),
                test_name TEXT,
                duration_seconds FLOAT,
                status TEXT
                );
                """)


            cur.execute("""
                CREATE TABLE IF NOT EXISTS defects (
                id SERIAL PRIMARY KEY,
                created_date DATE,
                severity TEXT,
                area TEXT,
                test_case_id INT
                );
                """)

        print("✅ Tables created successfully!")
