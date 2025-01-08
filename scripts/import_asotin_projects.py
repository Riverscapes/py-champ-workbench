"""
Script to update postgres with the GUIDs of Asotin projects that are already in
the Riverscapes Data Exchange. The CSV file used in this process was generated by
quering the data exchange using a script in the Riverscapes API workspace in this same repo.
Philip Bailey
7 Jan 2025
"""
import os
import csv
from pathlib import Path
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row


data_file = os.path.join(Path(__file__).resolve().parents[1], '..', 'asotin_projects.csv')

load_dotenv()

con = conn = psycopg.connect(
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
curs = con.cursor()

curs.execute('SELECT * FROM project_types WHERE description is not null')
project_types = {row['description']: row['project_type_id'] for row in curs.fetchall()}

# use CSV dict reader to load data from data_file and update the database
with open(data_file, 'r', encoding='utf8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        project_type = row['type']
        if project_type not in project_types:
            raise f"Project type '{project_type}' not found in database"

        curs.execute('UPDATE projects SET guid = %s, status_id = 5 WHERE visit_id = %s and project_type_id = %s', [
            row['guid'],
            row['visit_id'],
            project_types[project_type]
        ])

con.commit()
