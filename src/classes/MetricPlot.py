from classes.DBCon import db_connect


class MetricPlot():
    def __init__(self, plot_id: int, title: str, x_metric_id: int, y_metric_id: int, plot_type_id: int):
        self.plot_id = plot_id
        self.title = title
        self.x_metric_id = x_metric_id
        self.y_metric_id = y_metric_id
        self.plot_type_id = plot_type_id

    @staticmethod
    def load():

        conn = db_connect()
        curs = conn.cursor()
        curs.execute('SELECT * FROM metric_plots')
        rows = curs.fetchall()
        return [
            MetricPlot(
                row['plot_id'],
                row['title'],
                row['x_metric_id'],
                row['y_metric_id'],
                row['plot_type_id']
            ) for row in rows
        ]

    def __str__(self):
        return self.title
