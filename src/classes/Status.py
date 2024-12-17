from classes.DBCon import db_connect


class Status():
    def __init__(self, status_id: int, name: str):
        self.status_id = status_id
        self.name = name

    @staticmethod
    def load():
        conn = db_connect()
        curs = conn.cursor()
        curs.execute('SELECT * FROM statuses')
        rows = curs.fetchall()
        return [Status(row['status_id'], row['name']) for row in rows]
