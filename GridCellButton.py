from PySide import QtGui
from PySide.QtCore import QSignalMapper
from PySide.QtGui import QSizePolicy


class GridCellButton(QtGui.QPushButton):

    def __init__(self, stateType):
        super(GridCellButton, self).__init__()
        self.signalMapper = QSignalMapper(self)
        self.stateType = stateType
        self.setMinimumSize(5, 5)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def getStateType(self):
        return self._stateType

    def setStateType(self, stateType):
        if stateType in ["REGULAR", "WALL", "START", "GOAL"]:
            self._stateType = stateType
            if stateType == "REGULAR":
                self.setStyleSheet("QPushButton:hover {border: 2px dashed #262524;} QPushButton {background-color: white; border: 1px solid #262524;}")
            elif stateType == "WALL":
                self.setStyleSheet("QPushButton:hover {border: none;} QPushButton {background-color: white; border-image: url(images/wall-brick.gif); border: none;}")
                self.setText("")
            elif stateType == "START":
                self.setStyleSheet("QPushButton:hover {border: 2px dashed #262524;} QPushButton {background-color: white; border-image: url(images/agent-bw-b.png); border: 2px solid #262524;}")
                self.setText("")
            elif stateType == "GOAL":
                self.setStyleSheet("QPushButton:hover {border: 2px dashed #262524;} QPushButton {background-color: white; border-image: url(images/goal-bw-b.png); border: 2px solid #262524;}")
                self.setText("")
            else:
                return

    def resizeEvent(self, event):
        fontSize = max(event.size().width(), event.size().height()) * 0.25
        customFont = self.font()
        customFont.setPointSize(fontSize)
        self.setFont(customFont)

    stateType = property(getStateType, setStateType)
