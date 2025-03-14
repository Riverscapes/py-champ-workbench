import webbrowser
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableView, QHeaderView, QMenuBar, QMenu, QMessageBox, QDialog, QLineEdit, QSplitter, QLabel
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from models.ProjectsModel import ProjectsModel
from widgets.CheckedListBox import CheckedListBox
from classes.Watershed import Watershed
from classes.ProjectType import ProjectType
from classes.Status import Status
from classes.DBConProps import DBConProps
from dialogs.ProjectDialog import ProjectDialog
from dialogs.AssignStatusDialog import AssignStatusDialog


class ProjectsView(QWidget):

    on_data_changed = pyqtSignal()

    def __init__(self, db_con_props: DBConProps):
        super().__init__()

        main_hlayout = QHBoxLayout()
        # menu_bar = QMenuBar(self)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_hlayout.addWidget(splitter)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        splitter.addWidget(left_widget)
        splitter.setStretchFactor(0, 0)  # Fixed width for the left pane

        self.search = QLineEdit()
        self.search.setFixedWidth(200)
        self.search.setPlaceholderText("Visit ID or Site Name")
        self.search.textChanged.connect(self.load_data)
        left_layout.addWidget(self.search)

        watersheds = Watershed.load()
        watersheds.sort(key=lambda x: x.watershed_name)
        self.chk_watersheds = CheckedListBox([(w.watershed_id, w.watershed_name) for w in watersheds])
        self.chk_watersheds.on_check_changed.connect(self.load_data)
        left_layout.addWidget(self.chk_watersheds)

        self.chk_years = CheckedListBox([(y, str(y)) for y in range(2011, 2020)])
        self.chk_years.on_check_changed.connect(self.load_data)
        left_layout.addWidget(self.chk_years)

        statuses = Status.load()
        statuses.sort(key=lambda x: x.name)
        self.statuses = CheckedListBox([(s.status_id, s.name) for s in statuses])
        self.statuses.on_check_changed.connect(self.load_data)
        self.statuses.check_items_with_ids([1, 2, 3, 5, 6])
        left_layout.addWidget(self.statuses)

        project_types = ProjectType.load()
        project_types.sort(key=lambda x: x.name)
        self.project_types = CheckedListBox([(pt.project_type_id, pt.name) for pt in project_types])
        self.project_types.on_check_changed.connect(self.load_data)
        left_layout.addWidget(self.project_types)

        self.lbl_status = QLabel('')
        left_layout.addWidget(self.lbl_status)

        ########################################################################################################################
        # Right table layout

        self.table = QTableView()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableView.SelectionMode.MultiSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.doubleClicked.connect(self.handle_double_click)

        self.model = ProjectsModel(db_con_props)
        # self.account.currentIndexChanged.connect(self.on_filters_changed)
        self.table.setModel(self.model)
        self.table.setAlternatingRowColors(True)
        self.table.setColumnHidden(0, True)

        splitter.addWidget(self.table)
        splitter.setStretchFactor(1, 1)  # Stretch for the right pane

        # Force load of initial data
        self.load_data()

        self.setLayout(main_hlayout)

    def find_item_by_id(self, search_id: int):

        for row in range(self.model.rowCount()):
            if self.model.data(self.model.index(row, 0)) == search_id:
                return row

    def load_data(self, select_id: int = None) -> None:

        watershed_ids = [id for id, name in self.chk_watersheds.get_checked_items()]
        visit_years = [year for year, name in self.chk_years.get_checked_items()]
        statuses = [id for id, name in self.statuses.get_checked_items()]
        project_type_ids = [id for id, name in self.project_types.get_checked_items()]
        search = self.search.text()

        total = self.model.load_data(watershed_ids, visit_years, statuses, project_type_ids, search)
        percent = self.model.with_guid / total if total > 0 else 0
        self.lbl_status.setText(f"Projects shown: {total:,}\nProjects with GUIDs: {self.model.with_guid:,} ({percent:.0%})")
        # self.on_data_changed.emit()
        self.table.resizeColumnsToContents()

        if select_id is not None and isinstance(select_id, int) and select_id > 0:
            row = self.find_item_by_id(select_id)
            if row is not None and row >= 0:
                self.table.selectRow(row)
                self.table.scrollTo(self.model.index(row, 0))

    def handle_double_click(self, index):
        row = index.row()
        col = index.column()
        item_id = self.model.data(self.model.index(row, 0))

        if col == 6:
            guid = self.model.data(self.model.index(row, 6))
            if guid is not None and guid != '':
                url = f'https://data.riverscapes.net/p/{guid}'
                webbrowser.open(url)
        else:
            dialog = ProjectDialog(self.model.db_con_props, item_id)
            result = dialog.exec()
            if result == QDialog.DialogCode.Accepted:
                self.load_data(item_id)
                self.on_data_changed.emit()

    def show_context_menu(self, position: QPoint):
        # Get the index of the item that was clicked
        index = self.table.indexAt(position)

        if not index.isValid():
            return

        # Get the row number
        row = index.row()

        # Create the context menu
        context_menu = QMenu(self)

        # Add actions to the context menu
        action_assign_status = QAction('Assign Status', self)
        clear_selection = QAction('Clear Selection', self)
        clear_selection.triggered.connect(lambda: self.table.clearSelection())

        # Add actions to the menu
        context_menu.addAction(action_assign_status)
        context_menu.addAction(clear_selection)
        # Connect the actions to slots (you can define what should happen)
        action_assign_status.triggered.connect(lambda: self.assign_statis())

        # Show the context menu at the cursor position
        context_menu.exec(self.table.viewport().mapToGlobal(position))

    def assign_statis(self):

        selected_rows = self.table.selectionModel().selectedRows()
        project_ids = [self.model.data(self.model.index(row.row(), 0)) for row in selected_rows]
        dialog = AssignStatusDialog(self.model.db_con_props, project_ids)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
