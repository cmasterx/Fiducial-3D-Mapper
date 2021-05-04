# having trouble getting pyqt to work, not worth

import sys
import sip
from PyQt5.QtWidgets import QApplication
import pyqtgraph as pg
import numpy as np

app = QApplication(sys.argv)
pg.plot(x = np.linspace(0, 1, 10), y = np.linspace(1,20, 10), z=np.linspace(2,4, 10))
status = app.exec_()
sys.exit(status)
