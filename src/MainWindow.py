import os
import sys
from dotenv import load_dotenv
from PyQt6.QtWidgets import QApplication, QMainWindow, QMdiArea, QMdiSubWindow, QFileDialog, QMessageBox, QDialog
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import QSettings, Qt
from views.ProjectsView import ProjectsView
from dialogs.LoginDialog import LoginDialog
from classes.DBConProps import DBConProps

COMPANY_NAME = 'NorthArrowResearch'
APP_NAME = 'ChAMPWorkbench'

# Load variables from .env file
load_dotenv()


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.db_con_props = None

        self.mdi_area = QMdiArea()
        self.setCentralWidget(self.mdi_area)
        self.backup_required = False

        # Create menu of main views
        menu_bar = self.menuBar()

        self.file_menu = menu_bar.addMenu('File')
        action = QAction('Login', self)
        # action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        action.triggered.connect(self.login)
        self.file_menu.addAction(action)

        # Items that don't vary by database simply have 'None' as their data
        self.views_menu = menu_bar.addMenu('Views')
        self.add_main_view("Visits", None, self.open_visits, None)
        self.views_menu.addSeparator()

        #####################################################################################################################
        # Window menu
        window_menu = menu_bar.addMenu('Window')
        window_horizontal = QAction('Tile Horizontally', self)
        window_horizontal.triggered.connect(self.tile_windows_horizontally)
        window_menu.addAction(window_horizontal)

        window_vertical = QAction('Tile Vertically', self)
        window_vertical.triggered.connect(self.tile_windows_vertically)
        window_menu.addAction(window_vertical)

        self.setWindowTitle('CHaMP Workbench')
        self.setWindowIcon(QIcon('favicon.ico'))
        self.resize(800, 1000)

        self.open_visits()

        self.show()

    def login(self):

        if load_dotenv() is True:
            self.db_con_props = DBConProps(
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                db=os.getenv("DB_NAME"),
                root_cert=os.getenv("SSLROOTCERT"),
                client_cert=os.getenv("SSLCLIENTCERT"),
                ssl_key=os.getenv("SSLKEY")
            )
        else:
            settings = QSettings(COMPANY_NAME, APP_NAME)
            dialog = LoginDialog(settings, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                try:
                    con_props = DBConProps(
                        host=dialog.host.text(),
                        port=int(dialog.port.text()),
                        user=dialog.user.text(),
                        password=dialog.password.text(),
                        db=dialog.database.text(),
                        root_cert=dialog.root_cert.text(),
                        client_cert=dialog.client_cert.text(),
                        ssl_key=dialog.ssl_key.text()
                    )
                    conn = con_props.connect()
                    if conn is not None:
                        self.db_con_props = con_props
                        settings.setValue('host', dialog.host.text())
                        settings.setValue('port', dialog.port.text())
                        settings.setValue('database', dialog.database.text())
                        settings.setValue('user', dialog.user.text())
                        # settings.setValue('password', dialog.password.text())
                        settings.setValue('root_cert', dialog.root_cert.text())
                        settings.setValue('client_cert', dialog.client_cert.text())
                        settings.setValue('ssl_key', dialog.ssl_key.text())
                    else:
                        raise Exception('Failed to connect to database')
                except Exception as e:
                    QMessageBox.critical(self, 'Connection Error', str(e))

    def tile_windows_horizontally(self):

        sub_windows = self.mdi_area.subWindowList()
        open_windows = [sub_window for sub_window in sub_windows if sub_window.isVisible()]
        mdi_width = self.mdi_area.width()
        mdi_height = self.mdi_area.height()

        # Calculate the width for each subwindow
        if sub_windows:
            sub_window_width = mdi_width // len(open_windows)
            sub_window_height = mdi_height

            # Position each subwindow
            for i, sub_window in enumerate(open_windows):
                sub_window.setGeometry(i * sub_window_width, 0, sub_window_width, sub_window_height)

    def tile_windows_vertically(self):

        sub_windows = self.mdi_area.subWindowList()
        open_windows = [sub_window for sub_window in sub_windows if sub_window.isVisible()]
        mdi_width = self.mdi_area.width()
        mdi_height = self.mdi_area.height()

        # Calculate the height for each subwindow
        if sub_windows:
            sub_window_height = mdi_height // len(open_windows)
            sub_window_width = mdi_width  # Full width of the MDI area

            # Position each subwindow
            for i, sub_window in enumerate(open_windows):
                sub_window.setGeometry(0, i * sub_window_height, sub_window_width, sub_window_height)

    def on_data_changed(self):
        self.backup_required = True

    def open_visits(self):
        if self.db_con_props is None:
            self.login()
            if self.db_con_props is None:
                return
        self.open_subwindow(ProjectsView(self.db_con_props), 'Visits')

    def open_subwindow(self, widget, title):
        subwindow = QMdiSubWindow()
        subwindow.setWidget(widget)
        subwindow.setWindowTitle(title)
        self.mdi_area.addSubWindow(subwindow)
        # Check if there are no other subwindows open

        sub_windows = self.mdi_area.subWindowList()
        _visible_windows = [subwindow for subwindow in sub_windows if subwindow.isVisible()]
        # if len(visible_windows) <= 1:
        subwindow.showMaximized()
        # else:
        #     subwindow.show()

    def add_main_view(self, menu_text: str, action_data: str, callback, shortcut: str) -> None:
        """
        Add a menu item to the View menu

        menu_text: Display text for the menu item
        action_data: String used in the JSON key in the database setting to enable/disable menu item
        callback: Function that will be called when the menu item is triggered
        shortcut: Keyboard shortcut for the menu item
        """
        action = QAction(menu_text, self)
        action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        action.triggered.connect(callback)
        action.setData(action_data)

        if shortcut is not None:
            action.setShortcut(f'Ctrl+{shortcut}')

        self.views_menu.addAction(action)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
