from typing import List
from classes.DBCon import db_connect


class Project():

    def __init__(self, watershed_id: int, watershed_name: str, site_id: int, site_name: str, visit_id: int, visit_year: int, guid: str, project_id: int, project_type_id: int, project_type: str, status_id: int, status: str):
        self.watershed_id = watershed_id
        self.watershed_name = watershed_name
        self.site_id = site_id
        self.site_name = site_name
        self.visit_id = visit_id
        self.visit_year = visit_year
        self.guid = guid
        self.project_id = project_id
        self.project_type_id = project_type_id
        self.project_type = project_type
        self.status_id = status_id
        self.status = status

    @staticmethod
    def load(watershed_ids: List[int], visit_years: List[int], statuses: List[int], project_type_ids: List[int], search: str) -> list:
        params = [watershed_ids, visit_years, statuses, project_type_ids]
        search_filter = ''

        if search != '':
            search_filter = ' AND (%s IS NULL OR LOWER(site_name) LIKE LOWER(%s) OR visit_id::text = %s)'
            params.extend([None, f'%{search}%', search])

        query = f'''
            SELECT *
            FROM vw_projects
            WHERE (watershed_id = ANY(%s))
                AND (visit_year = ANY(%s))
                AND (status_id = ANY(%s))
                AND (project_type_id = ANY(%s))
                {search_filter}
        '''

        conn = db_connect()
        curs = conn.cursor()
        curs.execute(query, params)
        rows = curs.fetchall()
        return [Project(
            watershed_id=row['watershed_id'],
            watershed_name=row['watershed_name'],
            site_id=row['site_id'],
            site_name=row['site_name'],
            visit_id=row['visit_id'],
            visit_year=row['visit_year'],
            guid=row['guid'],
            project_id=row['project_id'],
            project_type_id=row['project_type_id'],
            project_type=row['project_type'],
            status_id=row['status_id'],
            status=row['status'],
        ) for row in rows]
