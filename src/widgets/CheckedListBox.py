from typing import List, Tuple
from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, pyqtSignal


class CheckedListBox(QWidget):

    # Custom signal that emits when item is checked or unchecked
    on_check_changed = pyqtSignal()

    def __init__(self, items: List[Tuple[int, str]], check_all: bool = False):
        super().__init__()

        # Create a QListWidget
        self.list_widget = QListWidget(self)

        # Create a dictionary to store the items keyed by name
        # so we can retrieve the IDs laters
        self.master_items = {name: i for i, name in items}

        # Add checkable items to the list
        # items = ["Option 1", "Option 2", "Option 3", "Option 4"]
        for __item_id, item_text in items:
            item = QListWidgetItem(item_text)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked if check_all is True else Qt.CheckState.Unchecked)
            self.list_widget.addItem(item)

        self.list_widget.itemClicked.connect(self.on_item_changed)

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.list_widget)
        self.setLayout(layout)

    def select_all(self):
        """Select all items in the list."""

        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setCheckState(Qt.CheckState.Checked)

    def select_none(self):
        """Deselect all items in the list."""

        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setCheckState(Qt.CheckState.Unchecked)

    def get_checked_items(self) -> List[Tuple[int, str]]:
        """Return a list of checked items."""

        checked_items = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                checked_items.append((self.master_items[item.text()], item.text()))
        return checked_items

    def on_item_changed(self, item):
        """Handle item check/uncheck event."""

        # print(f"{item.text()} is checked" if item.checkState() == Qt.CheckState.Checked else f"{item.text()} is unchecked")
        self.on_check_changed.emit()
