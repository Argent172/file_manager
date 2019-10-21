import os
import sys
from ctypes import windll
import string
import PyQt5
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, uic


class Main(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Main, self).__init__(parent)
        self.ui = uic.loadUi("main.ui")
        # --------------DRIVES---------------------
        bitmask = windll.kernel32.GetLogicalDrives()
        self.drives = []
        for letter in string.ascii_uppercase:
            if bitmask & 1:
                self.drives.append(letter + ":\\")
            bitmask >>= 1
        # ------------INITIALIZE--------------------
        self.widgets = [self.ui.widget, self.ui.widget_2, self.ui.widget_3, self.ui.widget_4]
        self.backButtons = [self.ui.backButton, self.ui.backButton_2, self.ui.backButton_3, self.ui.backButton_4]
        self.pathBoxes = [self.ui.pathBox, self.ui.pathBox_2, self.ui.pathBox_3, self.ui.pathBox_4]
        self.mainLists = [self.ui.mainList, self.ui.mainList_2, self.ui.mainList_3, self.ui.mainList_4]
        self.forwardButtons = [self.ui.forwardButton, self.ui.forwardButton_2,
                               self.ui.forwardButton_3, self.ui.forwardButton_4]
        self.backHistories = [[] for i in range(4)]
        self.paths = [-1 for i in range(4)]
        [i.hide() for i in self.widgets if i != self.ui.widget]
        # --------------CONNECT---------------------
        self.ui.Add_Frame.triggered.connect(self.add_frame)
        self.ui.Hide_Frame.triggered.connect(self.hide_frame)
        [i.lineEdit().returnPressed.connect(self.handle) for i in self.pathBoxes]
        [i.activated.connect(self.handle) for i in self.pathBoxes]
        [i.itemDoubleClicked.connect(self.handle) for i in self.mainLists]
        [i.clicked.connect(self.handle) for i in self.backButtons + self.forwardButtons]
        self.ui.Add_Frame.setShortcut('Ctrl+A')
        self.ui.Hide_Frame.setShortcut('Ctrl+H')
        self.ui.Exit_Action.setShortcut("Ctrl+Q")
        self.ui.Add_Frame.setStatusTip('Adding workspace-frame')
        self.ui.Hide_Frame.setStatusTip('Hiding workspace-frame')
        self.ui.Exit_Action.setStatusTip('Exit application')
        self.ui.Exit_Action.triggered.connect(qApp.quit)
        # -------------------------------------------
        self.updateboard(0)
        self.ui.Hide_Frame.setDisabled(True)
        self.ui.show()

    def add_frame(self):
        for i in self.widgets:
            if not i.isVisible():
                i.show()
                self.updateboard(self.widgets.index(i))
                break
        if self.widgets[3].isVisible():
            self.ui.Add_Frame.setDisabled(True)
        self.ui.Hide_Frame.setDisabled(False)

    def hide_frame(self):
        for i in list(reversed(self.widgets)):
            if i.isVisible() and i != self.ui.widget:
                i.hide()
                break
        if not self.widgets[1].isVisible():
            self.ui.Hide_Frame.setDisabled(True)
        self.ui.Add_Frame.setDisabled(False)

    def handle(self):

        if self.sender() in self.backButtons:
            focused = self.backButtons.index(self.sender())
            if self.paths[focused] != -1:
                self.backHistories[focused].append(self.paths[focused])
                if os.path.splitdrive(os.path.abspath(self.paths[focused]))[1] == "\\":
                    self.paths[focused] = -1
                else:
                    self.paths[focused] = os.path.dirname(self.paths[focused])
                self.updateboard(focused)

        if self.sender() in self.forwardButtons:
            focused = self.forwardButtons.index(self.sender())
            if self.backHistories[focused]:
                self.paths[focused] = self.backHistories[focused].pop()
                self.updateboard(focused)

        if self.sender() in self.mainLists:
            focused = self.mainLists.index(self.sender())
            self.backHistories[focused] = []
            if self.mainLists[focused].currentItem().text() in self.drives and self.paths[focused] == -1:
                self.paths[focused] = os.path.abspath(self.mainLists[focused].currentItem().text())
                self.updateboard(focused)
            else:
                newpath = os.path.abspath(self.paths[focused] + "\\" + os.listdir(self.paths[focused])[
                    self.mainLists[focused].currentRow()])

                if os.path.isdir(newpath):
                    self.paths[focused] = os.path.abspath(newpath)
                    self.updateboard(focused)
                    try:
                        os.startfile(newpath)
                    except OSError:
                        print("Operation cancelled by user")

        if self.sender() in self.pathBoxes:
            focused = self.pathBoxes.index(self.sender())
            newpath = os.path.abspath(self.pathBoxes[focused].currentText())

            if newpath != self.paths[focused]:
                self.backHistories[focused] = []
                if os.path.exists(newpath):
                    self.paths[focused] = newpath
                    self.updateboard(focused)
                else:
                    self.pathBoxes[focused].removeItem(0)


    def updateboard(self, board):

        if self.paths[board] == -1:
            self.mainLists[board].clear()
            self.mainLists[board].setFlow(0)
            self.mainLists[board].setViewMode(1)
            self.mainLists[board].setStyleSheet("""
            QListView {
            outline: 0;
            font-size: 25px;
            }
            QListWidget::item {
                border:none;
                text-decoration: none;
                padding-right: 200px;
                padding-top: 50px;
                padding-bottom: 50px;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 white, stop: 1 #e7e7e7);
                }
            QListWidget::item:selected {
            }
            QListWidget::item:selected:active {
                border: none;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #6a6ea9, stop: 1 #888dd9);
            }
            QListWidget::item:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #FAFBFE, stop: 1 #DCDEF1);
            }""")
            for i in self.drives:
                self.mainLists[board].addItem(i)
        else:
            try:
                os.chdir(self.paths[board])
            except PermissionError:
                self.paths[board] = os.path.dirname(self.paths[board])
                return self.warning()
            self.mainLists[board].clear()
            self.mainLists[board].setFlow(1)
            self.mainLists[board].setViewMode(0)
            self.mainLists[board].setStyleSheet("")

            for i in os.listdir():
                if os.path.isdir(os.getcwd() + "\\" + i):
                    self.mainLists[board].addItem("Folder: " + i)
                else:
                    self.mainLists[board].addItem("File:      " + i)

            if self.pathBoxes[board].findText(os.getcwd()) != -1:
                self.pathBoxes[board].removeItem(self.pathBoxes[board].findText(os.getcwd()))

            self.pathBoxes[board].insertItem(0, os.getcwd())
            self.pathBoxes[board].setCurrentText(os.getcwd())


    def warning(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setText("У Вас нет доступа к этой директории!")
        msgBox.setWindowTitle("Permission Warning")
        msgBox.setStandardButtons(QMessageBox.Cancel)
        msgBox.exec()


def my_excepthook(value, tback):
    print(str(value))


sys.excepthook = my_excepthook
app = QtWidgets.QApplication(sys.argv)
window = Main()
sys.exit(app.exec())
