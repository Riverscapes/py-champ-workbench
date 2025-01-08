import re
from PyQt6.QtWidgets import QComboBox
from PyQt6.QtCore import Qt
from classes.DBCon import db_connect


class DBCombo(QComboBox):

    def __init__(self,  sql: str):
        super().__init__()

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        pattern = r'SELECT (.+),(.+) FROM'
        match = re.match(pattern, sql)
        if match is None:
            raise ValueError('Invalid SQL statement')

        conn = db_connect()
        curs = conn.cursor()
        curs.execute(sql)
        for row in curs.fetchall():
            self.addItem(row[match[2].strip()], row[match[1].strip()])
