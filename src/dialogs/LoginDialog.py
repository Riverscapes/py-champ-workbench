import webbrowser
from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit, QMessageBox, QHBoxLayout, QPushButton
from PyQt6.QtCore import QSettings
from classes.Project import Project
from widgets.DBCombo import DBCombo
from dialogs.dialog_utilities import dialog_buttons

CONTROL_WIDTH = 500


class LoginDialog(QDialog):
    def __init__(self, settings: QSettings, parent=None):
        super().__init__(parent)

        self.setWindowTitle('Database Login')

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        form_layout = QFormLayout()
        main_layout.addLayout(form_layout)

        self.host = QLineEdit()
        self.host.setFixedWidth(CONTROL_WIDTH)
        form_layout.addRow('Host', self.host)

        self.port = QLineEdit()
        self.port.setFixedWidth(CONTROL_WIDTH)
        form_layout.addRow('Port', self.port)

        self.database = QLineEdit()
        self.database.setFixedWidth(CONTROL_WIDTH)
        form_layout.addRow('Database', self.database)

        self.user = QLineEdit()
        self.user.setFixedWidth(CONTROL_WIDTH)
        form_layout.addRow('User', self.user)

        self.password = QLineEdit()
        self.password.setFixedWidth(CONTROL_WIDTH)
        form_layout.addRow('Password', self.password)

        self.root_cert = QLineEdit()
        self.root_cert.setFixedWidth(CONTROL_WIDTH)
        form_layout.addRow('Root Certificate', self.root_cert)

        self.client_cert = QLineEdit()
        self.client_cert.setFixedWidth(CONTROL_WIDTH)
        form_layout.addRow('Client Certificate', self.client_cert)

        self.ssl_key = QLineEdit()
        self.ssl_key.setFixedWidth(CONTROL_WIDTH)
        form_layout.addRow('SSL Key', self.ssl_key)

        dialog_buttons(main_layout, self.accept, self.reject)

        if settings is not None:
            self.host.setText(settings.value('host'))
            self.port.setText(settings.value('port', '5432'))
            self.database.setText(settings.value('database'))
            self.user.setText(settings.value('user'))
            self.password.setText(settings.value('password'))
            self.root_cert.setText(settings.value('root_cert', ''))
            self.client_cert.setText(settings.value('client_cert', ''))
            self.ssl_key.setText(settings.value('ssl_key', ''))

    def accept(self):

        # Validate that all values have been entered
        if self.host.text().strip() == '' \
                or self.port.text().strip() == '' \
                or self.database.text().strip() == '' \
                or self.user.text().strip() == '' \
                or self.password.text().strip() == '':
            QMessageBox().critical(self, 'Error', 'All fields are required')
            return

        super().accept()
