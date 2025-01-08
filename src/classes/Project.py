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
        self.description = None

    @staticmethod
    def load(watershed_ids: List[int], visit_years: List[int], statuses: List[int], project_type_ids: List[int], search: str) -> list:
        params = [watershed_ids, visit_years, statuses, project_type_ids, project_type_ids]
        params = [len(watershed_ids), watershed_ids,
                  len(visit_years), visit_years,
                  len(statuses), statuses,
                  len(project_type_ids),  project_type_ids]

        search_filter = ''
        if search != '':
            search_filter = ' AND (%s IS NULL OR LOWER(site_name) LIKE LOWER(%s) OR visit_id::text = %s)'
            params.extend([None, f'%{search}%', search])

        query = f'''
            SELECT *
            FROM vw_projects
            WHERE (%s = 0 OR watershed_id = ANY(%s))
                AND (%s = 0 OR visit_year = ANY(%s))
                AND (%s = 0 OR status_id = ANY(%s))
                AND (%s = 0 OR project_type_id = ANY(%s))
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

    @staticmethod
    def save(project_id: int, status_id: int, guid: str, description: str) -> None:

        if guid == '':
            guid = None

        if description == '':
            description = None

        conn = db_connect()
        curs = conn.cursor()
        curs.execute('UPDATE projects SET status_id = %s, guid = %s, description = %s WHERE project_id = %s', (status_id, guid, description, project_id))
        conn.commit()

    @staticmethod
    def load_project_by_id(project_id: int) -> 'Project':
        conn = db_connect()
        curs = conn.cursor()
        curs.execute('SELECT * FROM vw_projects WHERE project_id = %s', (project_id,))
        row = curs.fetchone()
        return Project(
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
        )
