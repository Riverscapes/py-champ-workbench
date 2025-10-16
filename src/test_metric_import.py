import os
import argparse
from classes import MetricDefinition, DBCon
from psycopg import Cursor


def main():
    parser = argparse.ArgumentParser(description='Import metrics from XML file into the database.')
    parser.add_argument('xml_file', type=str, help='Path to the metrics XML file')
    args = parser.parse_args()

    metric_definitions = MetricDefinition.load(15, active_only=True)

    conn = DBCon.db_connect()
    curs = conn.cursor()

    try:
        MetricDefinition.import_from_xml(curs, metric_definitions, args.xml_file)
        print(f'Successfully imported metrics from {args.xml_file}')
    except Exception as e:
        print(f'Error importing metrics: {e}')


if __name__ == '__main__':
    main()
