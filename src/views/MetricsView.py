import webbrowser
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableView, QHeaderView, QMenuBar, QMenu, QMessageBox, QDialog, QLineEdit, QSplitter, QLabel, QComboBox
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from models.ProjectsModel import ProjectsModel
from widgets.CheckedListBox import CheckedListBox
from classes import Watershed, MetricPlot, db_connect, MetricDefinition
from classes.ProjectType import ProjectType
from classes.Status import Status
from classes.DBConProps import DBConProps
from dialogs.ProjectDialog import ProjectDialog
from dialogs.AssignStatusDialog import AssignStatusDialog
from classes.MatPlotLibChart import MplCanvas
from matplotlib.ticker import AutoMinorLocator, StrMethodFormatter


class MetricsView(QWidget):

    on_data_changed = pyqtSignal()

    def __init__(self, db_con_props: DBConProps):
        super().__init__()

        main_hlayout = QHBoxLayout()
        # menu_bar = QMenuBar(self)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_hlayout.addWidget(splitter)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        splitter.addWidget(left_widget)
        splitter.setStretchFactor(0, 0)  # Fixed width for the left pane

        self.search = QLineEdit()
        self.search.setFixedWidth(200)
        self.search.setPlaceholderText("Visit ID or Site Name")
        self.search.textChanged.connect(self.load_data)
        left_layout.addWidget(self.search)

        watersheds = Watershed.load()
        watersheds.sort(key=lambda x: x.watershed_name)
        self.chk_watersheds = CheckedListBox([(w.watershed_id, w.watershed_name) for w in watersheds])
        self.chk_watersheds.on_check_changed.connect(self.load_data)
        left_layout.addWidget(self.chk_watersheds)

        self.chk_years = CheckedListBox([(y, str(y)) for y in range(2011, 2020)])
        self.chk_years.on_check_changed.connect(self.load_data)
        left_layout.addWidget(self.chk_years)

        self.lbl_status = QLabel('')
        left_layout.addWidget(self.lbl_status)

        ########################################################################################################################
        # Right table layout

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(1, 1)  # Stretch the right pane

        self.metric_plots = MetricPlot.load()
        self.cbo_metric_plots = QComboBox()
        for plot in self.metric_plots:
            self.cbo_metric_plots.addItem(str(plot), plot)  # str(plot) is the display text, plot is the object
        self.cbo_metric_plots.currentIndexChanged.connect(self.load_data)
        right_layout.addWidget(self.cbo_metric_plots)

        self.sc = MplCanvas(self)  # , width=5, height=4, dpi=100)
        right_layout.addWidget(self.sc)

        self.metric_definitions = MetricDefinition.load(15, active_only=True)

        self.load_data()
        self.setLayout(main_hlayout)

    def load_data(self, select_id: int = None) -> None:

        plot: MetricPlot = self.cbo_metric_plots.currentData()
        if plot is None:
            return

        x_metric_name = next((md.title for md in self.metric_definitions if md.metric_id == plot.x_metric_id), 'Metric X')
        y_metric_name = next((md.title for md in self.metric_definitions if md.metric_id == plot.y_metric_id), 'Metric Y')

        watershed_ids = [id for id, name in self.chk_watersheds.get_checked_items()]
        visit_years = [year for year, name in self.chk_years.get_checked_items()]

        having_clause = ''
        if len(watershed_ids) > 0:
            having_clause += f' AND s.watershed_id IN ({",".join([str(id) for id in watershed_ids])})'

        if len(visit_years) > 0:
            having_clause += f' AND EXTRACT(YEAR FROM v.visit_date) IN ({",".join([str(year) for year in visit_years])})'

        conn = db_connect()
        curs = conn.cursor()
        curs.execute(f"""
            SELECT v.visit_id,
                s.watershed_id,
                MAX(CASE WHEN vm.metric_id = {plot.x_metric_id} THEN vm.metric_value END) AS x_value,
                MAX(CASE WHEN vm.metric_id = {plot.y_metric_id} THEN vm.metric_value END) AS y_value
            FROM visits v
                JOIN sites s ON v.site_id = s.site_id
                JOIN visit_metrics vm ON v.visit_id = vm.visit_id
            WHERE vm.metric_id IN ({plot.x_metric_id}, {plot.y_metric_id})
            GROUP BY v.visit_id, s.watershed_id
            HAVING 1 = 1 {having_clause}
        """)
        rows = curs.fetchall()

        x_values = [row['x_value'] for row in rows if row['x_value'] is not None and row['y_value'] is not None]
        y_values = [row['y_value'] for row in rows if row['x_value'] is not None and row['y_value'] is not None]
        self.sc.ax.clear()
        self.sc.ax.scatter(x_values, y_values, alpha=0.5)
        self.sc.ax.set_title(plot.title)
        self.sc.ax.set_xlabel(x_metric_name)
        self.sc.ax.set_ylabel(y_metric_name)
        self.sc.ax.xaxis.set_minor_locator(AutoMinorLocator())
        self.sc.ax.yaxis.set_minor_locator(AutoMinorLocator())
        self.sc.ax.xaxis.set_minor_formatter(StrMethodFormatter("{x:.1f}"))
        self.sc.ax.yaxis.set_minor_formatter(StrMethodFormatter("{x:.1f}"))
        self.sc.ax.grid(which='both', linestyle='--', linewidth=0.5)

        # Store visit IDs for tooltip display
        self.visit_ids = [row['visit_id'] for row in rows if row['x_value'] is not None and row['y_value'] is not None]
        self.annot = self.sc.ax.annotate("", xy=(0,0), xytext=(10,10), textcoords="offset points",
                                         bbox=dict(boxstyle="round", fc="white", ec="black", lw=0.5),
                                         arrowprops=dict(arrowstyle="->"))
        self.annot.set_visible(False)
        self.sc.ax.figure.canvas.mpl_connect("motion_notify_event", self.on_hover)
        self.sc.ax.figure.canvas.mpl_connect("axes_leave_event", self.on_leave)

    def on_hover(self, event):
        if event.inaxes == self.sc.ax:
            cont, ind = self.sc.ax.collections[0].contains(event)
            if cont:
                index = ind["ind"][0]
                x, y = self.sc.ax.collections[0].get_offsets()[index]
                visit_id = self.visit_ids[index] if index < len(self.visit_ids) else "N/A"
                self.annot.xy = (x, y)
                text = f"Visit ID: {visit_id}\nX: {x:.2f}\nY: {y:.2f}"
                self.annot.set_text(text)
                self.annot.set_visible(True)
                self.sc.draw()
            else:
                if self.annot.get_visible():
                    self.annot.set_visible(False)
                    self.sc.draw()

    def on_leave(self, event):
        self.annot.set_visible(False)
        self.sc.draw()
