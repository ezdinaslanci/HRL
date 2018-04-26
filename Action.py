
class Action:

    def __init__(self, actionType, coordinates):
        if actionType not in ["UP", "RIGHT", "DOWN", "LEFT"]:
            print("UNKNOWN TYPE")
        else:
            self.actionType = actionType
            self.coordinates = coordinates
            self.QValue = 0.0

    def getDestinationCoordinates(self):
        if self.actionType == "UP":
            return self.coordinates[0] - 1, self.coordinates[1]
        elif self.actionType == "RIGHT":
            return self.coordinates[0], self.coordinates[1] + 1
        elif self.actionType == "DOWN":
            return self.coordinates[0] + 1, self.coordinates[1]
        elif self.actionType == "LEFT":
            return self.coordinates[0], self.coordinates[1] - 1
        else:
            return

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return self.QValue < other.QValue
        return NotImplemented
