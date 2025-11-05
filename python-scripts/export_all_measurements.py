import argparse
import os
import json
import psycopg2
from psycopg2.extensions import cursor as Cursor


TABLES_TO_SKIP = [
    'crew',
    'visits',
    'sites',
    'statues',
    'projects',
    'project_types',
    'watersheds'
]

COLUMNS_TO_SKIP = [
    'programsiteid',
    'sitename',
    'watershedid',
    'watershedname',
    'sampledate',
    'hitchname',
    'crewname',
    'visityear',
    'iterationid',
    'categoryname',
    'panelname',
    'visitdate',
    'protocolid',
    'programid',
    'aem',
    'bug validation',
    'champ 10% revisit',
    'champ core',
    'champ-pibo comparison',
    'effectiveness',
    'has fish data',
    'imw',
    'remove',
    'velocity validation',
    'primary visit',
    'qc visit',
    'error',
    'no',
    'yes',
]


def export_all_measurements(curs, output_dir):

    # Get a list of all the tables in the public schema
    curs.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    tables = curs.fetchall()

    # Remove tables that we want to skip
    table_names = {table['table_name']: {'multirow': None, 'columns': []} for table in tables if table['table_name'] not in TABLES_TO_SKIP}

    for table_name in table_names.keys():
        # Get the columns for each table
        curs.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = %s", (table_name,))
        columns = curs.fetchall()
        table_names[table_name]['columns'] = [column['column_name'] for column in columns if column['column_name'] not in COLUMNS_TO_SKIP]

        # Get the maximum number of rows per visit across all tables
        curs.execute(f"""
            select max(tally)
            from (SELECT visitid, count(*) tally
            FROM {table_name}
            group by visitid))""")
        max_rows = curs.fetchone()
        table_names[table_name]['multirow'] = max_rows[0] > 1

    # Get all the visits that still require aux
    curs.execute("""
        SELECT v.visit_id
        FROM vw_projects p
                inner join visits v on p.visit_id = v.visit_id
                inner join sites s on v.site_id = s.site_id
                inner join watersheds w on s.watershed_id = w.watershed_id
        where project_type_id = 1
        and guid is not null
        and aux_uploaded is null
        order by w.name, v.visit_year""")

    visits = curs.fetchall()
    print(f"Found {len(visits)} visits that require aux data.")

    for visit in visits:
        visit_id = visit['id']
        visit_dir = os.path.join(output_dir, f"visit_{visit_id}")
        os.makedirs(visit_dir, exist_ok=True)

        for table in tables:
            table_name = table['table_name']
            if table_name in TABLES_TO_SKIP:
                continue

            curs.execute(f'SELECT * FROM {table_name} WHERE visit_id = %s', (visit_id,))
            for row in curs.fetchall():
                record_data = {key: value for key, value in row.items() if key not in COLUMNS_TO_SKIP}
                if len(record_data) > 0:
                    table_file = os.path.join(output_dir, visit_id, 'aux_measurements', f'{table_name}.json')
                    os.makedirs(os.path.dirname(table_file), exist_ok=True)
                    with open(os.path.join(table_file), 'w', encoding='utf-8') as json_file:
                        json.dump(record_data, json_file)

    print("All measurements have been exported to JSON files.")


def main():
    parser = argparse.ArgumentParser(description="Export all measurements from the database to JSON files.")
    parser.add_argument('db-service', type=str, required=True, help='Name of postgres service in .pg_service.conf to connect to the database.')
    parser.add_argument('output-dir', type=str, required=True, help='Directory to save the exported JSON files.')
    args = parser.parse_args()

    conn = psycopg2.connect(service=args.db_service)
    curs = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    export_all_measurements(curs, args.output_dir)


if __name__ == "__main__":
    main()
