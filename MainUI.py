#!/usr/bin/python
# -*- coding: utf-8 -*-

import glob
import sys
import os.path
import atexit

from PySide import QtCore
from PySide.QtCore import QSize

from RLTask import *
from Environment import *
from GridCellButton import GridCellButton
from ScientificDoubleSpinBox import ScientificDoubleSpinBox


class MainUI(QtGui.QMainWindow):

    def __init__(self):
        super(MainUI, self).__init__()

        sequenceFile = open("inp.dat", "w")
        sequenceFile.close()
        self.generateSequence = False
        self.resetLearning = True

        # initiate RLTask
        self.RLTask = RLTask(self)

        # frames
        self.leftFrame = QtGui.QFrame()
        self.rightFrame = QtGui.QFrame()
        self.bottomFrame = QtGui.QFrame()
        self.statusFrame = QtGui.QFrame()

        # stacked layout for multiple environments
        self.leftStackedLayout = QtGui.QStackedLayout()

        # other ui elements
        self.bottomGrid = QtGui.QHBoxLayout()
        self.bottomGrid.setContentsMargins(0, 0, 0, 0)
        self.mapNameLabel = QtGui.QLabel("")
        self.menuBar = self.menuBar()

        # initiate GUI
        self.initUI()

    def initUI(self):

        # central widget for QMainWindow, big boss
        centralWidget = QtGui.QWidget()
        self.setCentralWidget(centralWidget)

        # menu items
        loadMap = QtGui.QAction(QtGui.QIcon("images/open-bw.ico"), "Load Map", self)
        loadMap.setShortcut("Ctrl+O")
        loadMap.triggered.connect(self.loadMapFile)
        saveMap = QtGui.QAction(QtGui.QIcon("images/save-bw.png"), "Save Map", self)
        saveMap.setShortcut("Ctrl+S")
        saveMap.triggered.connect(self.saveMapFile)
        saveACopy = QtGui.QAction(QtGui.QIcon("images/saveACopy-bw.png"), "Save a Copy", self)
        saveACopy.triggered.connect(self.saveACopyFile)
        changeGridSize = QtGui.QAction(QtGui.QIcon("images/resize-bw.png"), "Grid Size", self)
        changeGridSize.setShortcut("Ctrl+G")
        changeGridSize.triggered.connect(self.changeGridSize)
        addNewEnv = QtGui.QAction(QtGui.QIcon("images/plus-bw.png"), "Add New", self)
        addNewEnv.setShortcut("Ctrl+N")
        addNewEnv.triggered.connect(self.addNewEnvironment)
        updateGridSS = QtGui.QAction(QtGui.QIcon("images/refresh-bw.png"), "Update SS", self)
        updateGridSS.triggered.connect(self.updateGridSS)
        reDrawGrid = QtGui.QAction(QtGui.QIcon("images/refresh-bw.png"), "Redraw Grid", self)
        reDrawGrid.triggered.connect(self.drawEnvironmentFromStateList)
        startQL = QtGui.QAction(QtGui.QIcon(""), "Start QL", self)
        startQL.triggered.connect(self.RLTask.QLThreadStart)
        startPS = QtGui.QAction(QtGui.QIcon(""), "Start PS", self)
        startPS.triggered.connect(self.RLTask.PSThreadStart)
        mapOps = self.menuBar.addMenu("&Map Operations")
        mapOps.addAction(loadMap)
        mapOps.addAction(saveMap)
        mapOps.addAction(saveACopy)
        gridOps = self.menuBar.addMenu("&Grid Operations")
        gridOps.addAction(changeGridSize)
        gridOps.addAction(addNewEnv)
        gridOps.addAction(updateGridSS)
        gridOps.addAction(reDrawGrid)
        trainingOps = self.menuBar.addMenu("&Training")
        trainingOps.addAction(startQL)
        trainingOps.addAction(startPS)

        # frame customization & layouts
        self.leftFrame.setStyleSheet("QFrame { background-color: wheat; border: 1px solid }")
        self.rightFrame.setStyleSheet("QFrame { background-color: transparent }")
        self.bottomFrame.setStyleSheet("QFrame { border-top: 1px solid #d1d1d1; border-bottom: 1px solid #d1d1d1; } QLabel { border: none; }")
        # self.statusFrame.setStyleSheet("QFrame { background-color: #d3d3d3; } QLabel { border: none; }")

        # leftFrame layout
        self.leftFrame.setLayout(self.leftStackedLayout)
        self.leftFrame.setMaximumWidth(819)

        # rightFrame widgets
        rightFrameWidgetWidth = 100
        alphaLabel = QtGui.QLabel("alpha: ")
        alphaSpinBox = QtGui.QDoubleSpinBox()
        alphaSpinBox.setRange(0, 1)
        alphaSpinBox.setSingleStep(0.01)
        alphaSpinBox.setValue(self.RLTask.alpha)
        alphaSpinBox.setFixedWidth(rightFrameWidgetWidth)
        alphaSpinBox.valueChanged.connect(lambda: self.RLTask.setAlpha(alphaSpinBox.value()))

        discountFactorLabel = QtGui.QLabel("discount factor: ")
        discountFactorSpinBox = QtGui.QDoubleSpinBox()
        discountFactorSpinBox.setRange(0, 1)
        discountFactorSpinBox.setSingleStep(0.01)
        discountFactorSpinBox.setValue(self.RLTask.discountFactor)
        discountFactorSpinBox.setFixedWidth(rightFrameWidgetWidth)
        discountFactorSpinBox.valueChanged.connect(lambda: self.RLTask.setDiscountFactor(discountFactorSpinBox.value()))

        maxEpsilonLabel = QtGui.QLabel("max epsilon: ")
        maxEpsilonSpinBox = QtGui.QDoubleSpinBox()
        maxEpsilonSpinBox.setRange(0, 1)
        maxEpsilonSpinBox.setSingleStep(0.01)
        maxEpsilonSpinBox.setValue(self.RLTask.maxEpsilon)
        maxEpsilonSpinBox.setFixedWidth(rightFrameWidgetWidth)
        maxEpsilonSpinBox.valueChanged.connect(lambda: self.RLTask.setMaxEpsilon(maxEpsilonSpinBox.value()))

        minEpsilonLabel = QtGui.QLabel("min epsilon: ")
        minEpsilonSpinBox = QtGui.QDoubleSpinBox()
        minEpsilonSpinBox.setRange(0, 1)
        minEpsilonSpinBox.setSingleStep(0.00001)
        minEpsilonSpinBox.setDecimals(5)
        minEpsilonSpinBox.setValue(self.RLTask.minEpsilon)
        minEpsilonSpinBox.setFixedWidth(rightFrameWidgetWidth)
        minEpsilonSpinBox.valueChanged.connect(lambda: self.RLTask.setMinEpsilon(minEpsilonSpinBox.value()))

        epsilonDecayFactorLabel = QtGui.QLabel("epsilon decay factor: ")
        epsilonDecayFactorSpinBox = QtGui.QDoubleSpinBox()
        epsilonDecayFactorSpinBox.setRange(0, 1)
        epsilonDecayFactorSpinBox.setSingleStep(0.00001)
        epsilonDecayFactorSpinBox.setDecimals(5)
        epsilonDecayFactorSpinBox.setValue(self.RLTask.epsilonDecayFactor)
        epsilonDecayFactorSpinBox.setFixedWidth(rightFrameWidgetWidth)
        epsilonDecayFactorSpinBox.valueChanged.connect(lambda: self.RLTask.setEpsilonDecayFactor(epsilonDecayFactorSpinBox.value()))

        epsilonDecayModeLabel = QtGui.QLabel("epsilon decay mode: ")
        epsilonDecayModeSpinBox = QtGui.QComboBox()
        epsilonDecayModeSpinBox.addItem("step")
        epsilonDecayModeSpinBox.addItem("episode")
        epsilonDecayModeSpinBox.setCurrentIndex(1)
        epsilonDecayModeSpinBox.setFixedWidth(rightFrameWidgetWidth)
        epsilonDecayModeSpinBox.currentIndexChanged.connect(lambda: self.RLTask.setEpsilonDecayMode(epsilonDecayModeSpinBox.currentText()))

        numOfUpdatesLabel = QtGui.QLabel("number of updates (PS): ")
        numOfUpdatesSpinBox = QtGui.QDoubleSpinBox()
        numOfUpdatesSpinBox.setRange(1, 50)
        numOfUpdatesSpinBox.setSingleStep(1)
        numOfUpdatesSpinBox.setDecimals(0)
        numOfUpdatesSpinBox.setValue(self.RLTask.numOfUpdates)
        numOfUpdatesSpinBox.setFixedWidth(rightFrameWidgetWidth)
        numOfUpdatesSpinBox.valueChanged.connect(lambda: self.RLTask.setNumOfUpdates(numOfUpdatesSpinBox.value()))

        priorityThresholdLabel = QtGui.QLabel("priority threshold (PS): ")
        priorityThresholdSpinBox = ScientificDoubleSpinBox()
        priorityThresholdSpinBox.setRange(0, 50)
        priorityThresholdSpinBox.setValue(self.RLTask.priorityThreshold)
        priorityThresholdSpinBox.setFixedWidth(rightFrameWidgetWidth)
        priorityThresholdSpinBox.valueChanged.connect(lambda: self.RLTask.setPriorityThreshold(priorityThresholdSpinBox.value()))

        RLParameterBox = QtGui.QGroupBox("RL Parameters")
        RLParameterBoxLayout = QtGui.QGridLayout()
        RLParameterBoxLayout.addWidget(alphaLabel, 0, 0)
        RLParameterBoxLayout.addWidget(alphaSpinBox, 0, 1)
        RLParameterBoxLayout.addWidget(discountFactorLabel, 1, 0)
        RLParameterBoxLayout.addWidget(discountFactorSpinBox, 1, 1)
        RLParameterBoxLayout.addWidget(maxEpsilonLabel, 2, 0)
        RLParameterBoxLayout.addWidget(maxEpsilonSpinBox, 2, 1)
        RLParameterBoxLayout.addWidget(minEpsilonLabel, 3, 0)
        RLParameterBoxLayout.addWidget(minEpsilonSpinBox, 3, 1)
        RLParameterBoxLayout.addWidget(epsilonDecayFactorLabel, 4, 0)
        RLParameterBoxLayout.addWidget(epsilonDecayFactorSpinBox, 4, 1)
        RLParameterBoxLayout.addWidget(epsilonDecayModeLabel, 5, 0)
        RLParameterBoxLayout.addWidget(epsilonDecayModeSpinBox, 5, 1)
        RLParameterBoxLayout.addWidget(numOfUpdatesLabel, 6, 0)
        RLParameterBoxLayout.addWidget(numOfUpdatesSpinBox, 6, 1)
        RLParameterBoxLayout.addWidget(priorityThresholdLabel, 7, 0)
        RLParameterBoxLayout.addWidget(priorityThresholdSpinBox, 7, 1)
        RLParameterBox.setLayout(RLParameterBoxLayout)

        trainUntilConvergenceCheckBox = QtGui.QCheckBox("train until convergence", self)
        trainUntilConvergenceCheckBox.toggle()
        trainUntilConvergenceCheckBox.stateChanged.connect(self.RLTask.toggleTrainUntilConvergenceOption)

        numOfEpisodesForTrainingLabel = QtGui.QLabel("train for (episodes) ")
        self.numOfEpisodesForTrainingSpinBox = QtGui.QDoubleSpinBox()
        self.numOfEpisodesForTrainingSpinBox.setRange(1, 100000)
        self.numOfEpisodesForTrainingSpinBox.setSingleStep(1)
        self.numOfEpisodesForTrainingSpinBox.setDecimals(0)
        self.numOfEpisodesForTrainingSpinBox.setValue(self.RLTask.numOfEpisodesForTraining)
        self.numOfEpisodesForTrainingSpinBox.setFixedWidth(rightFrameWidgetWidth)
        self.numOfEpisodesForTrainingSpinBox.setDisabled(True)
        self.numOfEpisodesForTrainingSpinBox.valueChanged.connect(lambda: self.RLTask.setNumOfEpisodesForTraining(self.numOfEpisodesForTrainingSpinBox.value()))

        convergenceIntervalLabel = QtGui.QLabel("convergence interval: ")
        convergenceIntervalSpinBox = QtGui.QDoubleSpinBox()
        convergenceIntervalSpinBox.setRange(5, 100)
        convergenceIntervalSpinBox.setSingleStep(1)
        convergenceIntervalSpinBox.setDecimals(0)
        convergenceIntervalSpinBox.setValue(self.RLTask.convergenceInterval)
        convergenceIntervalSpinBox.setFixedWidth(rightFrameWidgetWidth)
        convergenceIntervalSpinBox.valueChanged.connect(lambda: self.RLTask.setConvergenceInterval(convergenceIntervalSpinBox.value()))

        varianceThresholdLabel = QtGui.QLabel("variance threshold: ")
        varianceThresholdSpinBox = QtGui.QDoubleSpinBox()
        varianceThresholdSpinBox.setRange(0, 10)
        varianceThresholdSpinBox.setSingleStep(0.01)
        varianceThresholdSpinBox.setDecimals(2)
        varianceThresholdSpinBox.setValue(self.RLTask.varianceThreshold)
        varianceThresholdSpinBox.setFixedWidth(rightFrameWidgetWidth)
        varianceThresholdSpinBox.valueChanged.connect(lambda: self.RLTask.setConvergenceThreshold(varianceThresholdSpinBox.value()))

        RLTrainingBox = QtGui.QGroupBox("Training")
        RLTrainingBoxLayout = QtGui.QGridLayout()
        RLTrainingBoxLayout.addWidget(trainUntilConvergenceCheckBox, 0, 0)
        RLTrainingBoxLayout.addWidget(numOfEpisodesForTrainingLabel, 1, 0)
        RLTrainingBoxLayout.addWidget(self.numOfEpisodesForTrainingSpinBox, 1, 1)
        RLTrainingBoxLayout.addWidget(convergenceIntervalLabel, 2, 0)
        RLTrainingBoxLayout.addWidget(convergenceIntervalSpinBox, 2, 1)
        RLTrainingBoxLayout.addWidget(varianceThresholdLabel, 3, 0)
        RLTrainingBoxLayout.addWidget(varianceThresholdSpinBox, 3, 1)
        RLTrainingBox.setLayout(RLTrainingBoxLayout)

        generateSequenceFileCheckBox = QtGui.QCheckBox("generate action sequence file (inp.dat)", self)
        generateSequenceFileCheckBox.stateChanged.connect(self.toggleGenerateSequenceOption)

        resetLearningCheckBox = QtGui.QCheckBox("reset learning initially", self)
        resetLearningCheckBox.toggle()
        resetLearningCheckBox.stateChanged.connect(self.toggleResetLearningOption)

        otherOptionsBox = QtGui.QGroupBox("Other Options")
        otherOptionsBoxLayout = QtGui.QGridLayout()
        otherOptionsBoxLayout.addWidget(generateSequenceFileCheckBox, 0, 1)
        otherOptionsBoxLayout.addWidget(resetLearningCheckBox, 1, 1)
        otherOptionsBoxLayout.setRowStretch(2, 1)
        otherOptionsBox.setLayout(otherOptionsBoxLayout)

        # rightFrame layout
        rightGrid = QtGui.QGridLayout()
        rightGrid.addWidget(RLParameterBox, 0, 1)
        rightGrid.addWidget(RLTrainingBox, 1, 1)
        rightGrid.addWidget(otherOptionsBox, 2, 1)
        rightGrid.setRowStretch(0, 0)
        rightGrid.setRowStretch(1, 0)
        rightGrid.setRowStretch(2, 0)
        rightGrid.setRowStretch(2, 1)
        rightGrid.setColumnStretch(0, 1)
        rightGrid.setColumnStretch(1, 0)
        self.rightFrame.setLayout(rightGrid)

        # bottomFrame layout
        self.bottomGrid.setAlignment(QtCore.Qt.AlignLeft)
        self.bottomGrid.setContentsMargins(0, 10, 0, 10)
        self.bottomFrame.setLayout(self.bottomGrid)

        # statusFrame layout
        statusGrid = QtGui.QHBoxLayout()
        statusGrid.setContentsMargins(0, 0, 0, 0)
        statusGrid.addWidget(self.mapNameLabel)
        self.statusFrame.setLayout(statusGrid)

        # main window layout
        mainGrid = QtGui.QGridLayout()
        mainGrid.setColumnStretch(0, 1)
        mainGrid.setColumnStretch(1, 0)
        mainGrid.setRowStretch(0, 1)
        mainGrid.setRowStretch(1, 0)
        mainGrid.setRowStretch(2, 0)
        mainGrid.setColumnMinimumWidth(1, 215)
        mainGrid.setRowMinimumHeight(1, 100)
        mainGrid.setRowMinimumHeight(1, 25)
        mainGrid.setSpacing(10)
        mainGrid.setContentsMargins(10, 10, 10, 10)
        centralWidget.setLayout(mainGrid)
        mainGrid.addWidget(self.leftFrame, 0, 0)
        mainGrid.addWidget(self.rightFrame, 0, 1)
        mainGrid.addWidget(self.bottomFrame, 1, 0, 1, 2)
        mainGrid.addWidget(self.statusFrame, 2, 0, 1, 2)

        # create the first environment
        self.addNewEnvironment()

        # main window parameters
        self.setGeometry(600, 200, 775, 400)
        self.setWindowTitle("HRL-CD Experiment Software")
        # self.setWindowIcon(QtGui.QIcon("images/grid.png"))
        self.show()

    def updateGridSS(self):
        QtGui.QPixmap.grabWidget(self.leftStackedLayout.currentWidget()).save("ssGrid/env{0}.png".format(self.leftStackedLayout.currentIndex() + 1), "png")
        self.bottomGrid.itemAt(self.leftStackedLayout.currentIndex()).widget().setIcon(QtGui.QIcon("ssGrid/env{0}.png".format(self.leftStackedLayout.currentIndex() + 1)))
        self.bottomGrid.itemAt(self.leftStackedLayout.currentIndex()).widget().setIconSize(QSize(96, 96))

    # def resizeEvent(self, event):
    #     print(event.size())

    def toggleGenerateSequenceOption(self):
        self.generateSequence = not self.generateSequence

    def toggleResetLearningOption(self):
        self.resetLearning = not self.resetLearning

    def toggleNumOfEpisodesForTrainingSpinbox(self, state):
        self.numOfEpisodesForTrainingSpinBox.setDisabled(state)

    def drawEnvironmentFromStateList(self):
        self.clearEnvironment()
        environment = self.RLTask.environmentList[self.leftStackedLayout.currentIndex()]
        stateList = environment.stateList
        gridSize = (len(stateList), len(stateList[0]))
        environment.buttonList = np.empty(shape=gridSize, dtype=GridCellButton)
        separator1 = QtGui.QAction(self)
        separator1.setSeparator(True)
        separator2 = QtGui.QAction(self)
        separator2.setSeparator(True)
        for row in range(0, gridSize[0]):
            for col in range(0, gridSize[1]):
                newButton = GridCellButton(stateList[row][col].stateType)
                convertToRegular = QtGui.QAction(self)
                convertToRegular.setText("REGULAR")
                convertToRegular.setIcon(QtGui.QIcon("images/tick-bw.png"))
                convertToRegular.triggered.connect(lambda row=row, col=col: self.convertCell("REGULAR", row, col))
                convertToWall = QtGui.QAction(self)
                convertToWall.setText("WALL")
                convertToWall.setIcon(QtGui.QIcon("images/wall-bw.png"))
                convertToWall.triggered.connect(lambda row=row, col=col: self.convertCell("WALL", row, col))
                convertToStart = QtGui.QAction(self)
                convertToStart.setText("START")
                convertToStart.setIcon(QtGui.QIcon("images/start-bw.png"))
                convertToStart.triggered.connect(lambda row=row, col=col: self.convertCell("START", row, col))
                convertToGoal = QtGui.QAction(self)
                convertToGoal.setText("GOAL")
                convertToGoal.setIcon(QtGui.QIcon("images/goal-bw.png"))
                convertToGoal.triggered.connect(lambda row=row, col=col: self.convertCell("GOAL", row, col))
                printMaxAction = QtGui.QAction(self)
                printMaxAction.setText("MAX")
                printMaxAction.triggered.connect(lambda row=row, col=col: self.convertCell("MAX", row, col))
                newButton.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
                newButton.addAction(convertToRegular)
                newButton.addAction(convertToWall)
                newButton.addAction(separator1)
                newButton.addAction(convertToStart)
                newButton.addAction(convertToGoal)
                newButton.addAction(separator2)
                newButton.addAction(printMaxAction)
                # newButton.setText(stateList[row][col].getActionsStr())
                # newButton.setText(str(stateList[row][col].getMaxQValue()))
                newButton.clicked.connect(lambda row=row, col=col: self.convertCell("WALLSWITCH", row, col))
                environment.buttonList[row][col] = newButton
                self.leftStackedLayout.currentWidget().layout().addWidget(newButton, row, col)
        self.mapNameLabel.setText(environment.mapFileName)

    def showMaxActionsOnGrid(self):
        environment = self.RLTask.environmentList[self.leftStackedLayout.currentIndex()]
        buttonList = environment.buttonList
        stateList = environment.stateList
        gridSize = environment.gridSize
        for row in range(0, gridSize[0]):
            for col in range(0, gridSize[1]):
                maxAction = stateList[row][col].getMaxAction()
                if maxAction.QValue == 0:
                    buttonList[row][col].setText("")
                else:
                    if (row, col) != environment.startCoordinates and (row, col) != environment.goalCoordinates:
                        maxActionType = maxAction.actionType
                        if maxActionType == "UP":
                            buttonList[row][col].setText("↑")
                        elif maxActionType == "RIGHT":
                            buttonList[row][col].setText("→")
                        elif maxActionType == "DOWN":
                            buttonList[row][col].setText("↓")
                        elif maxActionType == "LEFT":
                            buttonList[row][col].setText("←")
                        else:
                            buttonList[row][col].setText("X")

    def loadMapFile(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self, "Select Map File", "mapFiles/", "GWMAPs (*.gwmap)")
        if os.path.isfile(fileName[0]):
            mapFile = open(fileName[0], "r")
            environment = self.RLTask.environmentList[self.leftStackedLayout.currentIndex()]
            environment.mapMatrix = np.loadtxt(mapFile)
            environment.gridSize = environment.mapMatrix.shape
            environment.mapFileName = fileName[0]
            mapFile.close()
            self.updateStateListFromMapMatrix()
            self.drawEnvironmentFromStateList()
            self.bottomGrid.itemAt(self.leftStackedLayout.currentIndex()).widget().animateClick()

    def saveMapFile(self):
        environment = self.RLTask.environmentList[self.leftStackedLayout.currentIndex()]
        if not os.path.isfile(environment.mapFileName):
            fileName = QtGui.QFileDialog.getSaveFileName(self, "Save file", "mapFiles/", "*.gwmap")
            if fileName[0]:
                fileNameToSave = fileName[0]
            else:
                return
        else:
            fileNameToSave = environment.mapFileName
        np.savetxt(fileNameToSave, np.matrix(environment.mapMatrix), fmt='%.0f')
        self.mapNameLabel.setText(fileNameToSave)
        environment.mapFileName = fileNameToSave
        QtGui.QMessageBox.information(self, "Information", "Map successfully saved.")

    def saveACopyFile(self):
        environment = self.RLTask.environmentList[self.leftStackedLayout.currentIndex()]
        fileName = QtGui.QFileDialog.getSaveFileName(self, "Save file", "mapFiles/", "*.gwmap")
        if fileName[0]:
            np.savetxt(fileName[0], np.matrix(environment.mapMatrix), fmt='%.0f')
            self.mapNameLabel.setText(fileName[0])
            QtGui.QMessageBox.information(self, "Information", "Map successfully saved.")
        else:
            return

    def updateMapMatrixFromStateList(self):
        environment = self.RLTask.environmentList[self.leftStackedLayout.currentIndex()]
        stateList = environment.stateList
        gridSize = environment.gridSize
        environment.mapMatrix = np.zeros(gridSize, dtype=np.int)
        for row in range(0, gridSize[0]):
            for col in range(0, gridSize[1]):
                if stateList[row][col].stateType == "REGULAR":
                    environment.mapMatrix[row, col] = 0
                elif stateList[row][col].stateType == "WALL":
                    environment.mapMatrix[row, col] = 1
                elif stateList[row][col].stateType == "START":
                    environment.mapMatrix[row, col] = 2
                elif stateList[row][col].stateType == "GOAL":
                    environment.mapMatrix[row, col] = -2
                else:
                    environment.mapMatrix[row, col] = 0

    def updateStateListFromMapMatrix(self):
        environment = self.RLTask.environmentList[self.leftStackedLayout.currentIndex()]
        mapMatrix = environment.mapMatrix
        gridSize = mapMatrix.shape
        environment.stateList = np.empty(shape=gridSize, dtype=State)
        stateList = environment.stateList
        for row in range(0, gridSize[0]):
            for col in range(0, gridSize[1]):
                if mapMatrix[row][col] == 0:
                    stateType = "REGULAR"
                elif mapMatrix[row][col] == 1:
                    stateType = "WALL"
                elif mapMatrix[row][col] == 2:
                    stateType = "START"
                    environment.startCoordinates = (row, col)
                elif mapMatrix[row][col] == -2:
                    stateType = "GOAL"
                    environment.goalCoordinates = (row, col)
                else:
                    stateType = "REGULAR"
                stateList[row][col] = State(stateType, (row, col), gridSize)
        self.deleteActionsHeadingWalls()

    def deleteActionsHeadingWalls(self):
        environment = self.RLTask.environmentList[self.leftStackedLayout.currentIndex()]
        gridSize = environment.gridSize
        stateList = environment.stateList
        for row in range(0, gridSize[0]):
            for col in range(0, gridSize[1]):
                if stateList[row][col].stateType == "WALL":
                    self.deleteActionsHeadingWall((row, col))

    def changeGridSize(self):
        text, ok = QtGui.QInputDialog.getText(self, 'Change Grid Size', 'Enter new size "row*col":')
        if ok:
            if str(text).count("*") == 1:
                newSize = str(text).strip().split("*", 2)
                if newSize[0].isdigit() and newSize[1].isdigit():
                    newSize = (int(newSize[0]), int(newSize[1]))
                    self.clearEnvironment()
                    self.RLTask.environmentList[self.leftStackedLayout.currentIndex()] = Environment(newSize)
                    self.drawEnvironmentFromStateList()
                    self.bottomGrid.itemAt(self.leftStackedLayout.currentIndex()).widget().animateClick()
                else:
                    QtGui.QMessageBox.critical(None, 'Exception', "Sizes should be positive integers.", QtGui.QMessageBox.Abort)
            else:
                QtGui.QMessageBox.critical(None, 'Exception', "Wrong input format.", QtGui.QMessageBox.Abort)

    def addNewEnvironment(self):
        self.RLTask.environmentList.append(Environment((5, 5)))
        envWid = QtGui.QWidget()
        leftGrid = QtGui.QGridLayout()
        leftGrid.setSpacing(0)
        leftGrid.setContentsMargins(0, 0, 0, 0)
        envWid.setLayout(leftGrid)
        self.leftStackedLayout.addWidget(envWid)
        envButton = QtGui.QPushButton()
        envButton.setFixedSize(100, 100)
        envButton.clicked.connect(lambda num=self.leftStackedLayout.count() - 1: self.changeEnvironment(num))
        self.bottomGrid.addWidget(envButton)
        self.leftStackedLayout.setCurrentIndex(self.leftStackedLayout.count() - 1)
        self.drawEnvironmentFromStateList()
        envButton.animateClick()

    def changeEnvironment(self, num):
        self.leftStackedLayout.setCurrentIndex(num)
        self.mapNameLabel.setText(self.RLTask.environmentList[self.leftStackedLayout.currentIndex()].mapFileName)
        for i in range(0, self.leftStackedLayout.count()):
            if i == num:
                self.bottomGrid.itemAt(i).widget().setStyleSheet("QPushButton { border: 2px dashed black}")
            else:
                self.bottomGrid.itemAt(i).widget().setStyleSheet("QPushButton { border: 2px solid black}")
        self.menuBar.findChildren(QtGui.QMenu)[1].actions()[2].trigger()

    def clearEnvironment(self):
        layoutToClear = self.leftStackedLayout.currentWidget().layout()
        for i in reversed(range(layoutToClear.count())):
            widgetToRemove = layoutToClear.itemAt(i).widget()
            layoutToClear.removeWidget(widgetToRemove)
            widgetToRemove.setParent(None)

    def deleteActionsHeadingWall(self, wallCoordinates):
        neighborList = []
        environment = self.RLTask.environmentList[self.leftStackedLayout.currentIndex()]
        gridSize = environment.gridSize
        stateList = environment.stateList
        if wallCoordinates[0] > 0:
            neighborList.append((wallCoordinates[0] - 1, wallCoordinates[1], "DOWN"))
        if wallCoordinates[0] < gridSize[0] - 1:
            neighborList.append((wallCoordinates[0] + 1, wallCoordinates[1], "UP"))
        if wallCoordinates[1] > 0:
            neighborList.append((wallCoordinates[0], wallCoordinates[1] - 1, "RIGHT"))
        if wallCoordinates[1] < gridSize[1] - 1:
            neighborList.append((wallCoordinates[0], wallCoordinates[1] + 1, "LEFT"))
        for neighbor in neighborList:
            stateList[neighbor[0]][neighbor[1]].deleteAction(neighbor[2])

    def addActionsHeadingRemovedWall(self, wallCoordinates):
        neighborList = []
        environment = self.RLTask.environmentList[self.leftStackedLayout.currentIndex()]
        gridSize = environment.gridSize
        stateList = environment.stateList
        if wallCoordinates[0] > 0:
            neighborList.append((wallCoordinates[0] - 1, wallCoordinates[1], "DOWN"))
        if wallCoordinates[0] < gridSize[0] - 1:
            neighborList.append((wallCoordinates[0] + 1, wallCoordinates[1], "UP"))
        if wallCoordinates[1] > 0:
            neighborList.append((wallCoordinates[0], wallCoordinates[1] - 1, "RIGHT"))
        if wallCoordinates[1] < gridSize[1] - 1:
            neighborList.append((wallCoordinates[0], wallCoordinates[1] + 1, "LEFT"))
        for neighbor in neighborList:
            stateList[neighbor[0]][neighbor[1]].addAction(neighbor[2])

    def convertCell(self, destType, row, col):
        environment = self.RLTask.environmentList[self.leftStackedLayout.currentIndex()]
        stateList = environment.stateList
        buttonList = environment.buttonList
        mapMatrix = environment.mapMatrix
        if stateList[row][col].stateType == "WALL" and destType != "WALL":
            self.addActionsHeadingRemovedWall((row, col))
        if destType == "REGULAR" or (destType == "WALLSWITCH" and stateList[row][col].stateType == "WALL"):
            if (row, col) == environment.startCoordinates:
                environment.startCoordinates = (None, None)
            if (row, col) == environment.goalCoordinates:
                environment.goalCoordinates = (None, None)
            stateList[row][col].stateType = "REGULAR"
            buttonList[row][col].stateType = "REGULAR"
            mapMatrix[row][col] = 0
        elif destType == "WALL" or (destType == "WALLSWITCH" and stateList[row][col].stateType == "REGULAR"):
            if (row, col) == environment.startCoordinates:
                environment.startCoordinates = (None, None)
            if (row, col) == environment.goalCoordinates:
                environment.goalCoordinates = (None, None)
            stateList[row][col].stateType = "WALL"
            buttonList[row][col].stateType = "WALL"
            mapMatrix[row][col] = 1
            self.deleteActionsHeadingWall((row, col))
        elif destType == "START":
            if (row, col) == environment.goalCoordinates:
                environment.goalCoordinates = (None, None)
            if environment.startCoordinates.count(None) == 0:
                currentStartCoordinates = environment.startCoordinates
                stateList[currentStartCoordinates[0]][currentStartCoordinates[1]].stateType = "REGULAR"
                buttonList[currentStartCoordinates[0]][currentStartCoordinates[1]].stateType = "REGULAR"
                mapMatrix[currentStartCoordinates[0]][currentStartCoordinates[1]] = 0
            environment.startCoordinates = (row, col)
            stateList[row][col].stateType = "START"
            buttonList[row][col].stateType = "START"
            mapMatrix[row][col] = 2
        elif destType == "GOAL":
            if (row, col) == environment.startCoordinates:
                environment.startCoordinates = (None, None)
            if environment.goalCoordinates.count(None) == 0:
                currentGoalCoordinates = environment.goalCoordinates
                stateList[currentGoalCoordinates[0]][currentGoalCoordinates[1]].stateType = "REGULAR"
                buttonList[currentGoalCoordinates[0]][currentGoalCoordinates[1]].stateType = "REGULAR"
                mapMatrix[currentGoalCoordinates[0]][currentGoalCoordinates[1]] = 0
            environment.goalCoordinates = (row, col)
            stateList[row][col].stateType = "GOAL"
            buttonList[row][col].stateType = "GOAL"
            mapMatrix[row][col] = -2
        elif destType == "MAX":
            print(stateList[row][col].getQValues())
        else:
            return
        self.menuBar.findChildren(QtGui.QMenu)[1].actions()[2].trigger()


def cleanSSFolder():
    files = glob.glob('ssGrid/*.png')
    for f in files:
        os.remove(f)

def main():
    app = QtGui.QApplication(sys.argv)
    app.setStyle("gtk")
    mainUI = MainUI()
    atexit.register(cleanSSFolder)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
