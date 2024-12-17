from classes.DBCon import db_connect


class Watershed():
    def __init__(self, watershed_id: int, watershed_name: str):
        self.watershed_id = watershed_id
        self.watershed_name = watershed_name

    @staticmethod
    def load():

        conn = db_connect()
        curs = conn.cursor()
        curs.execute('SELECT * FROM watersheds WHERE is_champ <> 0')
        rows = curs.fetchall()
        return [Watershed(row['watershed_id'], row['name']) for row in rows]

    def __str__(self):
        return self.watershed_name
