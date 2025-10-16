import matplotlib
matplotlib.use('QtAgg')  # For PyQt6

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        fig = Figure()
        self.ax = fig.add_subplot(111)
        super().__init__(fig)
        self.setParent(parent)

    def plot(self):
        self.ax.plot([0, 1, 2, 3], [0, 1, 4, 9])
        self.ax.set_title('Sample Plot')
        self.draw()