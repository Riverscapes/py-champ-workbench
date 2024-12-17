import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv


def db_connect():
    try:
        conn = psycopg.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            sslmode="require",
            sslrootcert=os.getenv("SSLROOTCERT"),
            sslcert=os.getenv("SSLCLIENTCERT"),
            sslkey=os.getenv("SSLKEY"),
            row_factory=dict_row
        )
        return conn
    except psycopg.OperationalError as e:
        print(f"Connection failed: {e}")

    return None
