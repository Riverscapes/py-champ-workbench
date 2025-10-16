from typing import List
import os
import argparse
import xml.etree.ElementTree as ET
import xml.dom.minidom
from psycopg import Cursor
from classes import DBCon


class MetricDefinition():
    def __init__(self, metric_id: int, title: str, xpath: str, result_xml_tag: str):
        self.metric_id = metric_id
        self.title = title
        self.xpath = xpath
        self.result_xml_tag = result_xml_tag

    @staticmethod
    def load(model_id: int = None, active_only: bool = False):

        conn = DBCon.db_connect()
        curs = conn.cursor()
        query = 'SELECT * FROM metric_definitions WHERE 1 = 1'
        params = []
        if model_id is not None:
            query += ' AND model_id = %s'
            params.append(model_id)
        if active_only:
            query += ' AND is_active <> 0'
        curs.execute(query, params)

        rows = curs.fetchall()
        return [MetricDefinition(
            row['metric_id'],
            row['title'],
            row['xpath'],
            row['result_xml_tag']
        ) for row in rows]

    def __str__(self):
        return f'{self.title} ({self.metric_id})'

    @staticmethod
    def import_from_xml(curs: Cursor, metric_definitions: list, xml_path: str):

        if not os.path.isfile(xml_path):
            raise FileNotFoundError(f'File not found: {xml_path}')

        tree = ET.parse(xml_path)
        root = tree.getroot()

        nod_visit_id = root.find('Meta/VisitID')
        if nod_visit_id is None or nod_visit_id.text is None:
            raise ValueError(f'No VisitID found in file {xml_path}')
        visit_id = int(nod_visit_id.text)

        curs.execute('SELECT title, tier_id FROM channel_unit_tiers')
        tier_mapping = {row['title'].replace(' ', '').replace('-', '').replace('/', ''): row['tier_id'] for row in curs.fetchall()}

        try:
            for metric_definition in metric_definitions:
                if metric_definition.xpath is None or metric_definition.xpath.strip() == '' or '*' in metric_definition.xpath:
                    continue

                print(f'Processing metric {metric_definition.title} from file {metric_definition.xpath}')
                search_xpath = metric_definition.xpath.replace('/TopoMetrics/', '')
                nod_value = root.find(search_xpath)

                if nod_value is None:
                    raise ValueError(f'No value found for metric {metric_definition.title} in file {xml_path}')

                value_text = nod_value.text
                if value_text is None or value_text.strip() == '':
                    value = None
                else:
                    try:
                        value = float(value_text)
                    except ValueError:
                        raise ValueError(f'Invalid value "{value_text}" for metric {metric_definition.title} in file {xml_path}')

                if 'ChannelUnitsTier' in metric_definition.xpath:
                    tier_name = metric_definition.xpath.split('/')[-2]
                    if tier_name is None:
                        raise ValueError(f'No tier name found for metric {metric_definition.title} in file {xml_path}')

                    tier_name = tier_name.replace(' ', '')
                    tier_id = tier_mapping.get(tier_name)
                    if tier_id is None:
                        raise ValueError(f'Unknown tier name "{tier_name}" for metric {metric_definition.title} in file {xml_path}')
                    curs.execute('INSERT INTO channel_unit_metrics (visit_id, tier_id, metric_id, metric_value) VALUES (%s, %s, %s, %s)', (visit_id, tier_id, metric_definition.metric_id, value))
                else:
                    curs.execute('INSERT INTO visit_metrics (visit_id, metric_id, metric_value) VALUES (%s, %s, %s)', (visit_id, metric_definition.metric_id, value))

            curs.connection.commit()
        except Exception as e:
            curs.connection.rollback()
            raise e


def main():
    parser = argparse.ArgumentParser(description='Import metrics from XML file into the database.')
    parser.add_argument('xml_file', type=str, help='Path to the metrics XML file')
    args = parser.parse_args()

    metric_definitions = MetricDefinition.load(active_only=True)

    conn = DBCon.db_connect()
    curs = conn.cursor()

    try:
        MetricDefinition.import_from_xml(curs, metric_definitions, args.xml_file)
        print(f'Successfully imported metrics from {args.xml_file}')
    except Exception as e:
        print(f'Error importing metrics: {e}')


if __name__ == '__main__':
    main()
