import webbrowser
from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit, QMessageBox, QHBoxLayout, QPushButton
from widgets.DBCombo import DBCombo
from dialogs.dialog_utilities import dialog_buttons
from classes.Project import Project
from classes.DBConProps import DBConProps

TIME_DELTA_WARNING = 30

CONTROL_WIDTH = 500

BASEL_URL = 'https://data.riverscapes.net'


class ProjectDialog(QDialog):
    def __init__(self, db_con_props: DBConProps, project_id: int, parent=None):
        super().__init__(parent)

        self.db_con_props = db_con_props
        self.setWindowTitle(f'Project Details ({project_id})')

        self.project: Project = Project.load_project_by_id(db_con_props, project_id)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        form_layout = QFormLayout()
        main_layout.addLayout(form_layout)

        form_layout.addRow('Watershed', QLabel(str(self.project.watershed_name)))
        form_layout.addRow('Site', QLabel(str(self.project.site_name)))
        form_layout.addRow('Visit ID', QLabel(str(self.project.visit_id)))
        form_layout.addRow('Year', QLabel(str(self.project.visit_year)))
        form_layout.addRow('Project Type', QLabel(str(self.project.project_type)))

        guid_layout = QHBoxLayout()
        self.guid = QLineEdit()
        guid_layout.addWidget(self.guid)
        self.guid.setFixedWidth(CONTROL_WIDTH)
        if self.project.guid is not None:
            self.guid.setText(self.project.guid)

        self.cmd_guid = QPushButton('Visit')
        self.cmd_guid.clicked.connect(self.visit_guid)
        guid_layout.addWidget(self.cmd_guid)

        form_layout.addRow('Data Exchange GUID', guid_layout)

        self.cbo_status = DBCombo('SELECT status_id, name FROM statuses ORDER BY name')
        self.cbo_status.setCurrentIndex(self.cbo_status.findData(self.project.status_id))
        self.cbo_status.setFixedWidth(CONTROL_WIDTH)
        form_layout.addRow('Status', self.cbo_status)

        self.description = QTextEdit()
        self.description.setFixedHeight(200)
        self.description.setFixedWidth(CONTROL_WIDTH)
        form_layout.addRow('Notes', self.description)
        if self.project.description is not None:
            self.description.setText(self.project.description)

        dialog_buttons(main_layout, self.accept, self.reject)
        self.guid_changed()
        self.guid.textChanged.connect(self.guid_changed)

    def visit_guid(self):
        if self.guid.text().strip() != '':
            url = f'{BASEL_URL}/p/{self.guid.text().strip()}'
            webbrowser.open(url)

    def guid_changed(self):
        self.cmd_guid.setEnabled(self.guid.text().strip() != '')

    def accept(self):

        description = self.description.toPlainText().strip()
        guid = self.guid.text().strip()
        status_id = self.cbo_status.currentData()

        if description != self.project.description or self.project.guid != guid or status_id != self.project.status_id:
            try:
                Project.save(self.db_con_props, self.project.project_id, status_id, guid, description)
            except Exception as e:
                QMessageBox().critical(self, 'Error', f'Error saving project: {e}')

        super().accept()
