from typing import List, Tuple
from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QVBoxLayout, QWidget, QMenu
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QAction


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

    def select_all(self, checked: bool):
        """Select all items in the list."""

        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setCheckState(Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)

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

    def check_items_with_ids(self, ids: List[int]):
        """Check items with the given IDs."""

        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if self.master_items[item.text()] in ids:
                item.setCheckState(Qt.CheckState.Checked)

    # def show_context_menu(self, position: QPoint):
    #     # Get the index of the item that was clicked
    #     index = self.table.indexAt(position)

    #     if not index.isValid():
    #         return

    #     # Get the row number
    #     row = index.row()

    #     # Assuming the first column has the TransactionID, adjust column index if needed
    #     transaction_id = self.model.data(self.model.index(row, 0))  # TransactionID assumed in column 0

    #     # Create the context menu
    #     context_menu = QMenu(self)

    #     # Add actions to the context menu
    #     select_all_action = QAction('Select All', self)
    #     selection_none_action = QAction('Select None', self)

    #     # Add actions to the menu
    #     context_menu.addAction(select_all_action)
    #     context_menu.addAction(selection_none_action)

    #     # Connect the actions to slots (you can define what should happen)
    #     select_all_action.triggered.connect(lambda: self.select_all(True))
    #     selection_none_action.triggered.connect(lambda: self.select_all(False))

    #     # Show the context menu at the cursor position
    #     context_menu.exec(self.table.viewport().mapToGlobal(position))

    def contextMenuEvent(self, event):
        context_menu = QMenu(self)

        select_all_action = QAction("Select All", self)
        select_all_action.triggered.connect(lambda: self.select_all(True))
        context_menu.addAction(select_all_action)

        select_none_action = QAction("Select None", self)
        select_none_action.triggered.connect(lambda: self.select_all(False))
        context_menu.addAction(select_none_action)

        context_menu.exec(self.mapToGlobal(event.pos()))
