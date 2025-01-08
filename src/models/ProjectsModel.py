from typing import List, Tuple
from datetime import datetime
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PyQt6.QtGui import QColor
from classes.Project import Project


class ProjectsModel(QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self._data: List[Project] = []
        self._header = ['ProjectID', 'Watershed', 'Site',  'Year', 'VisitID', 'Project Type', 'GUID']

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
        self._data = Project.load(watershed_ids, visit_years, statuses, project_type_ids, search)
        self.endResetModel()
        return len(self._data)

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._header)
