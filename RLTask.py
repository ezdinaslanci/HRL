from statistics import variance
from threading import Thread

from PySide import QtGui
from collections import deque

from PQueue import PQueue


class RLTask:

    def __init__(self, mainUI):
        self.mainUI = mainUI
        self.environmentList = []

        # RL parameters
        self.alpha = 0.2
        self.discountFactor = 0.90
        self.maxEpsilon = 0.35
        self.minEpsilon = 0.00001
        self.epsilonDecayFactor = 0.99992
        self.epsilonDecayMode = "episode"
        self.currentEpsilon = self.maxEpsilon
        self.actionDictionary = {"LEFT": "1", 'UP': "2", "RIGHT": "3", "DOWN": "4"}

        # PS parameters
        self.PQueue = PQueue()
        self.priorityThreshold = 0.0000000001
        self.numOfUpdates = 15

        # training parameters
        self.trainUntilConvergence = True
        self.numOfEpisodesForTraining = 1000

        # convergence parameters
        self.convergenceInterval = 15
        self.varianceThreshold = 0.3
        self.lastNStepsQueue = deque(maxlen=self.convergenceInterval)

    def getMaxEpsilon(self):
        return self._maxEpsilon

    def setMaxEpsilon(self, maxEpsilon):
        self._maxEpsilon = maxEpsilon

    def getMinEpsilon(self):
        return self._minEpsilon

    def setMinEpsilon(self, minEpsilon):
        self._minEpsilon = minEpsilon

    def setAlpha(self, alpha):
        self.alpha = alpha

    def setDiscountFactor(self, discountFactor):
        self.discountFactor = discountFactor

    def setEpsilonDecayFactor(self, epsilonDecayFactor):
        self.epsilonDecayFactor = epsilonDecayFactor

    def setEpsilonDecayMode(self, epsilonDecayMode):
        self.epsilonDecayMode = epsilonDecayMode

    def setNumOfUpdates(self, numOfUpdates):
        self.numOfUpdates = numOfUpdates

    def setPriorityThreshold(self, priorityThreshold):
        self.priorityThreshold = priorityThreshold

    def setConvergenceInterval(self, convergenceInterval):
        self.convergenceInterval = int(convergenceInterval)
        self.lastNStepsQueue = deque(maxlen=self.convergenceInterval)

    def setConvergenceThreshold(self, convergenceThreshold):
        self.varianceThreshold = convergenceThreshold

    def toggleTrainUntilConvergenceOption(self):
        self.trainUntilConvergence = not self.trainUntilConvergence
        self.mainUI.toggleNumOfEpisodesForTrainingSpinbox(self.trainUntilConvergence)

    def setNumOfEpisodesForTraining(self, numOfEpisodesForTraining):
        self.numOfEpisodesForTraining = numOfEpisodesForTraining

    maxEpsilon = property(getMaxEpsilon, setMaxEpsilon)
    minEpsilon = property(getMinEpsilon, setMinEpsilon)

    def QLThreadStart(self):
        self.QLThread = Thread(target=self.applyQLearning)
        self.QLThread.start()

    def PSThreadStart(self):
        self.PSThread = Thread(target=self.applyPrioritizedSweeping)
        self.PSThread.start()

    def applyQLearning(self):

        environmentNum = self.mainUI.leftStackedLayout.currentIndex()
        environment = self.environmentList[environmentNum]
        stateList = environment.stateList

        if environment.startCoordinates.count(None) + environment.goalCoordinates.count(None) > 0:
            QtGui.QMessageBox.critical(None, "Missing Parameters", "Please set start and goal states.")
            return

        if self.mainUI.resetLearning:
            environment.resetLearning()
            self.lastNStepsQueue.clear()
            sequenceFile = open("inp.dat", "w")
            sequenceFile.close()

        numOfEpisodes = numOfActionsInEpisode = totalNumOfActions = 0
        self.currentEpsilon = self.maxEpsilon

        if self.mainUI.generateSequence:
            actionSequence = []

        # episode loop
        while True:

            agentCurrentCoordinates = self.environmentList[environmentNum].startCoordinates
            numOfEpisodes += 1
            numOfActionsInEpisode = 0

            # if len(self.lastNStepsQueue) == self.convergenceInterval:
            #     print("episode %d, variance: %f" % (numOfEpisodes, variance(self.lastNStepsQueue)))

            # action loop
            while agentCurrentCoordinates != self.environmentList[environmentNum].goalCoordinates:
                currentState = stateList[agentCurrentCoordinates[0]][agentCurrentCoordinates[1]]
                chosenAction = currentState.getAction(self.currentEpsilon)
                destinationCoordinates = chosenAction.getDestinationCoordinates()
                nextState = stateList[destinationCoordinates[0]][destinationCoordinates[1]]
                chosenAction.QValue += self.alpha * (nextState.immReward + self.discountFactor * nextState.getMaxQValue() - chosenAction.QValue)
                agentCurrentCoordinates = destinationCoordinates
                numOfActionsInEpisode += 1
                if self.mainUI.generateSequence:
                    actionSequence.append(self.actionDictionary[chosenAction.actionType])
                if self.epsilonDecayMode == "step" and self.currentEpsilon > self.minEpsilon:
                    self.currentEpsilon *= self.epsilonDecayFactor

            self.lastNStepsQueue.append(numOfActionsInEpisode)
            totalNumOfActions += numOfActionsInEpisode
            if self.epsilonDecayMode == "episode" and self.currentEpsilon > self.minEpsilon:
                self.currentEpsilon *= self.epsilonDecayFactor

            if not self.trainUntilConvergence and numOfEpisodes >= self.numOfEpisodesForTraining:
                print("QL trained for %d episodes, %d actions, optimal* path has %d actions." % (numOfEpisodes, totalNumOfActions, min(self.lastNStepsQueue)))
                self.mainUI.showMaxActionsOnGrid()
                if self.mainUI.generateSequence:
                    sequenceFile = open("inp.dat", "a")
                    for action in actionSequence:
                        sequenceFile.write("%s\n" % action)
                    sequenceFile.close()
                break

            if self.trainUntilConvergence and len(self.lastNStepsQueue) == self.convergenceInterval and variance(self.lastNStepsQueue) <= self.varianceThreshold:
                print("QL converged in %d episodes, %d actions, optimal* path has %d actions." % (numOfEpisodes, totalNumOfActions, min(self.lastNStepsQueue)))
                self.mainUI.showMaxActionsOnGrid()
                if self.mainUI.generateSequence:
                    sequenceFile = open("inp.dat", "a")
                    for action in actionSequence:
                        sequenceFile.write("%s\n" % action)
                    sequenceFile.close()
                break

    def applyPrioritizedSweeping(self):

        environmentNum = self.mainUI.leftStackedLayout.currentIndex()
        environment = self.environmentList[environmentNum]
        stateList = environment.stateList

        if environment.startCoordinates.count(None) + environment.goalCoordinates.count(None) > 0:
            QtGui.QMessageBox.critical(None, "Missing Parameters", "Please set start and goal states.")
            return

        if self.mainUI.resetLearning:
            environment.resetLearning()
            self.lastNStepsQueue.clear()
            self.PQueue.clear()
            sequenceFile = open("inp.dat", "w")
            sequenceFile.close()

        numOfEpisodes = numOfActionsInEpisode = totalNumOfActions = 0
        self.currentEpsilon = self.maxEpsilon

        if self.mainUI.generateSequence:
            actionSequence = []

        # episode loop
        while True:

            agentCurrentCoordinates = self.environmentList[environmentNum].startCoordinates
            numOfEpisodes += 1
            numOfActionsInEpisode = 0

            # print(self.PQueue.count())
            # self.mainUI.showMaxActionsOnGrid()

            # action loop
            while agentCurrentCoordinates != self.environmentList[environmentNum].goalCoordinates:
                currentState = stateList[agentCurrentCoordinates[0]][agentCurrentCoordinates[1]]
                chosenAction = currentState.getAction(self.currentEpsilon)
                destinationCoordinates = chosenAction.getDestinationCoordinates()
                nextState = stateList[destinationCoordinates[0]][destinationCoordinates[1]]
                priority = abs(nextState.immReward + self.discountFactor * nextState.getMaxQValue() - chosenAction.QValue)

                # if self.PQueue.count() == 0:
                    # chosenAction.QValue += self.alpha * (nextState.immReward + self.discountFactor * nextState.getMaxQValue() - chosenAction.QValue)

                self.insertToModel(chosenAction, nextState, nextState.immReward)
                self.insertToPQueue(chosenAction, priority)

                agentCurrentCoordinates = destinationCoordinates
                numOfActionsInEpisode += 1
                if self.mainUI.generateSequence:
                    actionSequence.append(self.actionDictionary[chosenAction.actionType])
                if self.epsilonDecayMode == "step" and self.currentEpsilon > self.minEpsilon:
                    self.currentEpsilon *= self.epsilonDecayFactor

                for n in range(int(self.numOfUpdates)):
                    if self.PQueue.ifEmpty():
                        break
                    bestAction = self.PQueue.pop()
                    destinationCoordinates = bestAction.getDestinationCoordinates()
                    nextState = stateList[destinationCoordinates[0]][destinationCoordinates[1]]
                    bestAction.QValue += self.alpha * (nextState.immReward + self.discountFactor * nextState.getMaxQValue() - bestAction.QValue)
                    self.sweep(nextState)

            self.lastNStepsQueue.append(numOfActionsInEpisode)
            totalNumOfActions += numOfActionsInEpisode
            if self.epsilonDecayMode == "episode" and self.currentEpsilon > self.minEpsilon:
                self.currentEpsilon *= self.epsilonDecayFactor

            if not self.trainUntilConvergence and numOfEpisodes >= self.numOfEpisodesForTraining:
                print("PS trained for %d episodes, %d actions, optimal* path has %d actions." % (numOfEpisodes, totalNumOfActions, min(self.lastNStepsQueue)))
                self.mainUI.showMaxActionsOnGrid()
                if self.mainUI.generateSequence:
                    sequenceFile = open("inp.dat", "a")
                    for action in actionSequence:
                        sequenceFile.write("%s\n" % action)
                    sequenceFile.close()
                break

            if self.trainUntilConvergence and len(self.lastNStepsQueue) == self.convergenceInterval and variance(self.lastNStepsQueue) <= self.varianceThreshold:
                print("PS converged in %d episodes, %d actions, optimal* path has %d actions." % (numOfEpisodes, totalNumOfActions, min(self.lastNStepsQueue)))
                self.mainUI.showMaxActionsOnGrid()
                if self.mainUI.generateSequence:
                    sequenceFile = open("inp.dat", "a")
                    for action in actionSequence:
                        sequenceFile.write("%s\n" % action)
                    sequenceFile.close()
                break

    def insertToModel(self, chosenAction, nextState, reward):
        model = self.environmentList[self.mainUI.leftStackedLayout.currentIndex()].model
        # if not (chosenAction, nextState, reward) in model:
        #     model.append((chosenAction, nextState, reward))
        if nextState not in model:
            model[nextState] = {}
            model[nextState][chosenAction] = reward

    def insertToPQueue(self, chosenAction, priority):
        if priority >= self.priorityThreshold:
            self.PQueue.push(chosenAction, priority)
            # print("---------------------------------")
            # self.PQueue.print()

    def calculatePriority(self, chosenAction, nextState):
        return abs(nextState.immReward + self.discountFactor * nextState.getMaxQValue() - chosenAction.QValue)

    def findEntryInModelHeadingState(self, coordinates):
        model = self.environmentList[self.mainUI.leftStackedLayout.currentIndex()].model
        indexList = [i for i, entry in enumerate(model) if entry[1].coordinates == coordinates]
        returnList = []
        for index in indexList:
            returnList.append(model[index])
        return returnList

    def sweep(self, state):
        model = self.environmentList[self.mainUI.leftStackedLayout.currentIndex()].model
        # indexList = [i for i, entry in enumerate(model) if entry[1] == state]
        # for index in indexList:
        #     (actionFromModel, nextStateFromModel, rewardFromModel) = model[index]
        #     priority = abs(rewardFromModel + self.discountFactor * nextStateFromModel.getMaxQValue() - actionFromModel.QValue)
        #     self.insertToPQueue(actionFromModel, priority)
        actionsLeadingToStateDict = model[state]
        for action in actionsLeadingToStateDict:
            rewardFromModel = actionsLeadingToStateDict[action]
            priority = abs(rewardFromModel + self.discountFactor * state.getMaxQValue() - action.QValue)
