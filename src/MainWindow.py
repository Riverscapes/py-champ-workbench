import os
import sys
import re
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from PyQt6.QtWidgets import QApplication, QMainWindow, QMdiArea, QMdiSubWindow, QFileDialog, QMessageBox, QDialog
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QSettings, QEvent, Qt
from views.ProjectsView import ProjectsView

COMPANY_NAME = 'NorthArrowResearch'
APP_NAME = 'ChAMPWorkbench'

# Load variables from .env file
load_dotenv()


class MainWindow(QMainWindow):

    def __init__(self, access_token=None, account_id=None):
        super().__init__()

        self.access_token = access_token
        self.account_id = account_id

        self.mdi_area = QMdiArea()
        self.setCentralWidget(self.mdi_area)
        self.backup_required = False

        # Create menu of main views
        menu_bar = self.menuBar()

        self.file_menu = menu_bar.addMenu('File')

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
        self.resize(800, 1000)

        self.db_path = None
        settings = QSettings(COMPANY_NAME, APP_NAME)
        # db_path = settings.value(LAST_DATABASE, type=str)
        # if db_path is not None and os.path.isfile(db_path):
        #     self.open_db(db_path)

        self.open_visits()

        self.show()

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
        self.open_subwindow(ProjectsView(self.db_path), 'Visits')

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

env_access_token = os.getenv('HARVEST_ACCESS_TOKEN')
env_account_id = os.getenv('HARVEST_ACCOUNT_ID')

window = MainWindow(env_access_token, env_account_id)
window.show()
app.exec()
