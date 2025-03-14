from typing import List
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PyQt6.QtGui import QColor
from classes.Project import Project
from classes.DBConProps import DBConProps


class ProjectsModel(QAbstractTableModel):
    def __init__(self, db_con_props: DBConProps):
        super().__init__()
        self.db_con_props = db_con_props
        self._data: List[Project] = []
        self._header = ['ProjectID', 'Watershed', 'Site',  'Year', 'VisitID', 'Project Type', 'GUID']
        self.with_guid = 0

    def data(self, index, role: int = Qt.ItemDataRole.DisplayRole):

        if not index.isValid():
            return None  # or an appropriate default value

        if role == Qt.ItemDataRole.DisplayRole:
            item: Project = self._data[index.row()]
            if index.column() == 0:
                return item.project_id
            if index.column() == 1:
                return item.watershed_name
            if index.column() == 2:
                return item.site_name
            if index.column() == 3:
                return item.visit_year
            if index.column() == 4:
                return item.visit_id
            if index.column() == 5:
                return item.project_type
            if index.column() == 6:
                return item.guid

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self._header[section]

    def load_data(self, watershed_ids: List[int], visit_years: List[int], statuses: List[int], project_type_ids: List[int], search: str,) -> int:

        self.beginResetModel()
        self.with_guid = 0
        self._data = Project.load(self.db_con_props, watershed_ids, visit_years, statuses, project_type_ids, search)
        self.with_guid = sum([1 for project in self._data if project.guid is not None])
        self.endResetModel()
        return len(self._data)

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._header)
