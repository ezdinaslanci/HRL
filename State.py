import random
from operator import attrgetter

from Action import Action


class State:

    def __init__(self, stateType, coordinates, gridSize):

        self.stateType = stateType
        self.gridSize = gridSize

        # state parameters
        self.actionList = []
        self.coordinates = coordinates
        self.betCen = 0

        self.generateActionSet()

    def generateActionSet(self):
        if self.coordinates[0] > 0:
            self.actionList.append(Action("UP", self.coordinates))
        if self.coordinates[0] < self.gridSize[0] - 1:
            self.actionList.append(Action("DOWN", self.coordinates))
        if self.coordinates[1] > 0:
            self.actionList.append(Action("LEFT", self.coordinates))
        if self.coordinates[1] < self.gridSize[1] - 1:
            self.actionList.append(Action("RIGHT", self.coordinates))

    def addAction(self, actionType):
        if not any(action.actionType == actionType for action in self.actionList):
            self.actionList.append(Action(actionType, self.coordinates))

    def deleteAction(self, actionType):
        if any(action.actionType == actionType for action in self.actionList):
            index = self.actionList.index(next(action for action in self.actionList if action.actionType == actionType))
            del self.actionList[index]

    def getAction(self, epsilon):
        maxAction = max(self.actionList, key=attrgetter('QValue'))
        if maxAction.QValue == 0:
            return random.choice(self.actionList)
        elif random.uniform(0, 1) <= epsilon:
            return random.choice(self.actionList)
            # TODO exclude max
        else:
            return maxAction

    def getFairAction(self, epsilon):
        maxAction = max(self.actionList, key=attrgetter('QValue'))
        maxActionList = []
        nonMaxActionList = []
        for action in self.actionList:
            if action.QValue == maxAction.QValue:
                maxActionList.append(action)
            else:
                nonMaxActionList.append(action)
        if nonMaxActionList and random.uniform(0, 1) <= epsilon:
            return random.choice(nonMaxActionList)
        else:
            return random.choice(maxActionList)



    def getMaxQValue(self):
        if len(self.actionList) > 0:
            return max(action.QValue for action in self.actionList)

    def getMaxAction(self):
        if len(self.actionList) > 0:
            return max(self.actionList, key=attrgetter('QValue'))

    def getActionsStr(self):
        strAct = ""
        if any(action.actionType == "UP" for action in self.actionList):
            strAct += "U"
        if any(action.actionType == "DOWN" for action in self.actionList):
            strAct += "D"
        if any(action.actionType == "LEFT" for action in self.actionList):
            strAct += "L"
        if any(action.actionType == "RIGHT" for action in self.actionList):
            strAct += "R"
        return strAct

    def getQValues(self):
        QList = {}
        for action in self.actionList:
            QList[action.actionType] = action.QValue
        return QList

    def getStateType(self):
        return self._stateType

    def setStateType(self, stateType):
        if stateType in ["REGULAR", "WALL", "GOAL", "START"]:
            self._stateType = stateType
            if stateType == "GOAL":
                self.immReward = 100
            else:
                self.immReward = 0

    stateType = property(getStateType, setStateType)
