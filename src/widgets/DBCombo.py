import sqlite3
from PyQt6.QtWidgets import QComboBox
from PyQt6.QtCore import Qt


class DBCombo(QComboBox):

    def __init__(self, db_path: str, sql: str):
        super().__init__()

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            for row in cursor.fetchall():
                self.addItem(row[1], row[0])
