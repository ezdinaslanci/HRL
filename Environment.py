import numpy as np

from GridCellButton import GridCellButton
from State import State


class Environment:

    def __init__(self, gridSize):

        # grid size
        self.gridSize = gridSize

        # data holders
        self.stateList = np.empty(shape=self.gridSize, dtype=State)
        self.buttonList = np.empty(shape=self.gridSize, dtype=GridCellButton)
        self.mapMatrix = np.zeros(self.gridSize, dtype=np.int)
        self.mapFileName = "unsavedMap"
        self.model = {}

        self.startCoordinates = (None, None)
        self.goalCoordinates = (None, None)

        # construct stateList
        for row in range(0, self.gridSize[0]):
            for col in range(0, self.gridSize[1]):
                self.stateList[row, col] = State("REGULAR", (row, col), self.gridSize)

    def resetLearning(self):
        for row in range(0, self.gridSize[0]):
            for col in range(0, self.gridSize[1]):
                for action in self.stateList[row][col].actionList:
                    action.QValue = 0
