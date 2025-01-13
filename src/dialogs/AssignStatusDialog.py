from typing import List
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QMessageBox
from widgets.DBCombo import DBCombo
from dialogs.dialog_utilities import dialog_buttons
from classes.DBConProps import DBConProps

CONTROL_WIDTH = 500


class AssignStatusDialog(QDialog):
    def __init__(self, db_con_props: DBConProps, project_ids: List[int], parent=None):
        super().__init__(parent)

        self.db_con_props = db_con_props
        self.setWindowTitle(f'Assign Status to {len(project_ids)} Projects')
        self.project_ids = project_ids

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        form_layout = QFormLayout()
        main_layout.addLayout(form_layout)

        self.cbo_status = DBCombo('SELECT status_id, name FROM statuses ORDER BY name')
        # self.cbo_status.setCurrentIndex(self.cbo_status.findData(self.project.status_id))
        self.cbo_status.setFixedWidth(CONTROL_WIDTH)
        form_layout.addRow('New status', self.cbo_status)

        dialog_buttons(main_layout, self.accept, self.reject)

    def accept(self):

        status_id = self.cbo_status.currentData()

        # Show a QMessageBox asking if user wants to proceed
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setText(f'Assign status to {len(self.project_ids)} projects?')
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.No)
        ret = msg.exec()

        if ret == QMessageBox.StandardButton.No:
            return

        conn = self.db_con_props.connect()
        curs = conn.cursor()
        try:
            curs.execute('UPDATE projects SET status_id = %s WHERE project_id = ANY(%s)', (status_id, self.project_ids))
            conn.commit()
            super().accept()
        except Exception as e:
            conn.rollback()
            QMessageBox().critical(self, 'Error', f'Error saving project: {e}')
