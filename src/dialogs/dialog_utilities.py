import os
from datetime import datetime, timedelta
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QSpacerItem, QSizePolicy
from PyQt6.QtCore import QDate
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt


def dialog_buttons(parent_layout: QVBoxLayout, accept_callback, reject_callback, save_eanbled: bool = True) -> None:

    button_layout = QHBoxLayout()

    spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    button_layout.addItem(spacer)

    # Add a button to close the dialog
    close_button = QPushButton("Save")
    close_button.clicked.connect(accept_callback)
    close_button.setEnabled(save_eanbled)

    if save_eanbled is True:
        close_button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    button_layout.addWidget(close_button)

    cancel_button = QPushButton("Cancel")

    if reject_callback is not None:
        cancel_button.clicked.connect(reject_callback)
    cancel_button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    button_layout.addWidget(cancel_button)

    parent_layout.addLayout(button_layout)


def load_button_icon(button: QPushButton, icon_file_name: str) -> None:
    icon_path = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'icons', f'{icon_file_name}.svg')
    if not os.path.exists(icon_path):
        raise ValueError(f'Icon missing at path {icon_path}')

    icon = QIcon(icon_path)
    button.setIcon(icon)
    button.setText('')
    button.setIconSize(button.size())


def qdate_to_sqlite(date: QDate) -> str:
    full_date = datetime(date.year(), date.month(), date.day(), datetime.now().hour, datetime.now().minute, datetime.now().second)
    return full_date.strftime('%Y-%m-%d %H:%M:%S')


def get_last_month() -> tuple[datetime, datetime]:
    now = datetime.now()
    from_date = now.replace(month=now.month - 1 if now.month > 1 else 12)
    from_date = from_date.replace(day=1)
    from_date = from_date.replace(year=from_date.year if from_date.month != 12 else from_date.year - 1)

    to_date = now.replace(day=1)
    to_date = to_date - timedelta(days=1)

    return from_date, to_date
