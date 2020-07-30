from PyQt5.QtWidgets import QApplication, QLabel
from win32api import GetKeyState

app = QApplication([])

label = QLabel('Hello World!')

app.setWindowFlags(QtCore.Qt.Tool)

label.show()
app.exec_()
