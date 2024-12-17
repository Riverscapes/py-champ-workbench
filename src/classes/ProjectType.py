from classes.DBCon import db_connect


class ProjectType():
    def __init__(self, project_type_id: int, name: str):
        self.project_type_id = project_type_id
        self.name = name

    @staticmethod
    def load():

        conn = db_connect()
        curs = conn.cursor()
        curs.execute('SELECT * FROM project_types WHERE is_visit_level <> 0')
        rows = curs.fetchall()
        return [ProjectType(row['project_type_id'], row['name']) for row in rows]

    def __str__(self):
        return self.name
