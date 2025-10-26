import math
from collections import defaultdict
import numpy as np
from PyQt6.QtWidgets import QWidget, QHBoxLayout
from PyQt6.QtCore import pyqtSignal
from classes import db_connect
from classes.MatPlotLibChart import MplCanvas

QUERIES = {
    "topo_status": """
        SELECT 
            v.watershed_id,
            v.watershed_name,
            v.visit_year,
            COUNT(*) AS total_count,
            COUNT(CASE WHEN p.guid IS NOT NULL THEN 1 END) AS with_guid
        FROM vw_visits v
        INNER JOIN projects p ON v.visit_id = p.visit_id
        INNER JOIN watersheds w ON v.watershed_id = w.watershed_id
        WHERE w.is_champ <> 0 and p.project_type_id = 1
        GROUP BY v.watershed_id, v.watershed_name, v.visit_year
        ORDER BY v.watershed_name, v.visit_year;
        """
}

class StatusView(QWidget):

    on_data_changed = pyqtSignal()

    def __init__(self, sql_key: str, parent: QWidget) -> None:
        super().__init__(parent)

        main_hlayout = QHBoxLayout()
        self.sql_query = QUERIES[sql_key]

        self.sc = MplCanvas(self)  # , width=5, height=4, dpi=100)
        main_hlayout.addWidget(self.sc)
        self.setLayout(main_hlayout)

        self.load_data()

    def load_data(self) -> None:

        dbcon = db_connect()
        curs = dbcon.cursor()
        data = curs.execute(self.sql_query).fetchall()

        # Convert to nested dict: {watershed_name: {year: (with_guid, without_guid)}}
        grouped = {}
        for row in data:
            without_guid = row['total_count'] - row['with_guid']
            grouped.setdefault(row['watershed_name'], {})[row['visit_year']] = (row['with_guid'], without_guid)

        # Clear previous plot
        self.sc.ax.clear()

        # Compute max for shared y-axis (including totals)
        max_count = max(
            sum(vals) for ws_data in grouped.values() for vals in ws_data.values()
        )

        # Compute totals across all watersheds
        totals_by_year = defaultdict(lambda: [0, 0])  # {year: [with_guid, without_guid]}
        for ws_data in grouped.values():
            for year, (with_guid, without_guid) in ws_data.items():
                totals_by_year[year][0] += with_guid
                totals_by_year[year][1] += without_guid

        # Prepare grid layout: add 1 extra chart for totals
        ncols = 3
        num_ws = len(grouped) + 1  # extra chart for totals
        nrows = math.ceil(num_ws / ncols)

        fig = self.sc.figure
        fig.clf()

        # Plot individual watersheds
        for idx, (name, years_data) in enumerate(grouped.items(), start=1):
            ax = fig.add_subplot(nrows, ncols, idx)
            years = sorted(years_data.keys())
            with_guid_vals = [years_data[y][0] for y in years]
            without_guid_vals = [years_data[y][1] for y in years]
            x = np.arange(len(years))

            ax.bar(x, with_guid_vals, color="#4CAF50")
            ax.bar(x, without_guid_vals, bottom=with_guid_vals, color="#D3D3D3")

            ax.legend_.remove() if ax.get_legend() else None
            ax.yaxis.grid(True, color="#EEEEEE")
            ax.set_ylim(0, max_count * 1.1)
            ax.set_xticks(x)
            ax.set_xticklabels(years, rotation=45)
            ax.set_ylabel("Count")

            ax.set_title(name)
            total_with_guid = sum(with_guid_vals)
            total_records = total_with_guid + sum(without_guid_vals)
            pct = (total_with_guid / total_records * 100) if total_records else 0
            # ax.text(0.5, 1.05, f"{pct:.1f}% with GUID", transform=ax.transAxes,
            #         ha='center', va='bottom', fontsize=10, fontweight='bold')

            ax.set_title(f"{name} {pct:.1f}% with Topo Project")

        # Plot totals across all watersheds
        ax = fig.add_subplot(nrows, ncols, num_ws)
        years = sorted(totals_by_year.keys())
        with_guid_vals = [totals_by_year[y][0] for y in years]
        without_guid_vals = [totals_by_year[y][1] for y in years]
        x = np.arange(len(years))
        max_count = max(with_guid + without_guid for with_guid, without_guid in zip(with_guid_vals, without_guid_vals))

        ax.bar(x, with_guid_vals, color="#4CAF50")
        ax.bar(x, without_guid_vals, bottom=with_guid_vals, color="#D3D3D3")

        ax.legend_.remove() if ax.get_legend() else None
        ax.yaxis.grid(True, color="#EEEEEE")
        ax.set_ylim(0, max_count * 1.1)
        ax.set_xticks(x)
        ax.set_xticklabels(years, rotation=45)
        ax.set_ylabel("Count")

        # ax.set_title("Totals Across All Watersheds")
        total_with_guid = sum(with_guid_vals)
        total_records = total_with_guid + sum(without_guid_vals)
        pct = (total_with_guid / total_records * 100) if total_records else 0
        # ax.text(0.5, 1.05, f"{pct:.1f}% with GUID", transform=ax.transAxes,
        #         ha='center', va='bottom', fontsize=10, fontweight='bold')

        ax.set_title(f"All Watersheds {pct:.1f}% with Topo Project")

        # Hide any remaining empty subplots
        total_subplots = nrows * ncols
        for idx in range(num_ws + 1, total_subplots + 1):
            ax = fig.add_subplot(nrows, ncols, idx)
            ax.axis('off')

        fig.tight_layout(pad=2.0, h_pad=1.5)
        self.sc.draw()
