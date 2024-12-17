from typing import List, Tuple
from datetime import datetime, timedelta
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableView, QHeaderView, QMenuBar, QMenu, QMessageBox, QDialog, QApplication, QPushButton, QLineEdit
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from classes.DBCon import db_connect
from models.ProjectsModel import ProjectsModel
from widgets.CheckedListBox import CheckedListBox
from classes.Watershed import Watershed
from classes.ProjectType import ProjectType
from classes.Status import Status


class ProjectsView(QWidget):

    on_data_changed = pyqtSignal()

    def __init__(self, db_path: str):
        super().__init__()

        conn = db_connect()
        curs = conn.cursor()
        curs.execute("SELECT * FROM visits")
        self.visits = curs.fetchall()

        main_hlayout = QHBoxLayout()
        menu_bar = QMenuBar(self)

        left_layout = QVBoxLayout()
        main_hlayout.addLayout(left_layout)

        self.search = QLineEdit()
        self.search.setFixedWidth(200)
        self.search.setPlaceholderText("Visit ID or Site Name")
        left_layout.addWidget(self.search)

        watersheds = Watershed.load()
        watersheds.sort(key=lambda x: x.watershed_name)
        self.chk_watersheds = CheckedListBox([(w.watershed_id, w.watershed_name) for w in watersheds])
        self.chk_watersheds.on_check_changed.connect(self.on_filters_changed)
        left_layout.addWidget(self.chk_watersheds)

        self.chk_years = CheckedListBox([(y, str(y)) for y in range(2011, 2020)])
        self.chk_years.on_check_changed.connect(self.on_filters_changed)
        left_layout.addWidget(self.chk_years)

        statuses = Status.load()
        statuses.sort(key=lambda x: x.name)
        self.statuses = CheckedListBox([(s.status_id, s.name) for s in statuses])
        self.statuses.on_check_changed.connect(self.on_filters_changed)
        left_layout.addWidget(self.statuses)

        project_types = ProjectType.load()
        project_types.sort(key=lambda x: x.name)
        self.project_types = CheckedListBox([(pt.project_type_id, pt.name) for pt in project_types])
        self.project_types.on_check_changed.connect(self.on_filters_changed)
        left_layout.addWidget(self.project_types)

        ########################################################################################################################
        # Right table layout

        self.table = QTableView()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        # self.table.doubleClicked.connect(self.handle_double_click)

        self.model = ProjectsModel()
        # self.account.currentIndexChanged.connect(self.on_filters_changed)
        self.table.setModel(self.model)
        self.table.setAlternatingRowColors(True)
        self.table.setColumnHidden(0, True)

        # Force load of initial data
        self.on_filters_changed()

        main_hlayout.addWidget(self.table)
        self.setLayout(main_hlayout)

    def on_filters_changed(self):

        watershed_ids = [id for id, name in self.chk_watersheds.get_checked_items()]
        visit_years = [year for year, name in self.chk_years.get_checked_items()]
        statuses = [id for id, name in self.statuses.get_checked_items()]
        project_type_ids = [id for id, name in self.project_types.get_checked_items()]
        search = self.search.text()

        self.model.load_data(watershed_ids, visit_years, statuses, project_type_ids, search)
        self.on_data_changed.emit()
        self.table.resizeColumnsToContents()
