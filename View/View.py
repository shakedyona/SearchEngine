import configparser
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox, QFileDialog,  QMainWindow, QApplication, QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout
from PyQt5.QtWidgets import (QPushButton, QLineEdit, QLabel, QCheckBox, QComboBox)
from PyQt5.QtCore import pyqtSlot
from PyQt5 import QtCore
import sys

from Controller import Controller


class StartWindow(QWidget):
    def __init__(self):
        super(StartWindow, self).__init__()
        QWidget.__init__(self)
        self.path_document = ''
        self.path_to_save = ''
        self.lbl = QLabel("", self)
        self.Checked = False

        self.button_start = QPushButton("Start")
        self.button_reset = QPushButton("Reset")
        self.button_Load_dictionary = QPushButton("Load the dictionary to path")
        self.button_display_dictionary = QPushButton("display dictionary")
        self.text = QLabel("")
        self.text.setAlignment(Qt.AlignCenter)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.button_Load_dictionary)
        self.layout.addWidget(self.button_start)
        self.layout.addWidget(self.button_display_dictionary)
        self.layout.addWidget(self.button_reset)
        self.setLayout(self.layout)

        self.button_Load_dictionary.clicked.connect(self.LoadDictionery)
        self.button_start.clicked.connect(self.start)
        self.button_display_dictionary.clicked.connect(self.DisplayDictionary)
        self.button_reset.clicked.connect(self.Reset)

        # stemming
        self.b = QCheckBox("stemming?", self)
        self.b.stateChanged.connect(self.clickBox)
        self.b.move(20, 150)
        self.b.resize(320, 40)

        # text box documents 1.1
        self.textbox_documents = QLineEdit(self)
        self.textbox_documents.move(20, 20)
        self.textbox_documents.resize(280, 40)

        # text box to save
        self.textbox_to_save = QLineEdit(self)
        self.textbox_to_save.move(20, 85)
        self.textbox_to_save.resize(280, 40)

        # button to inside text to document
        self.button_textbox_documents = QPushButton('Browse path of document', self)
        self.button_textbox_documents.move(350, 25)
        self.button_textbox_documents.resize(250, 40)

        # button to inside text - path to save on
        self.button_textbox_to_save = QPushButton('Browse path to save on', self)
        self.button_textbox_to_save.move(350, 85)
        self.button_textbox_to_save.resize(250, 40)

        # connect button to function on_click
        self.button_textbox_documents.clicked.connect(self.on_click_document)
        self.button_textbox_to_save.clicked.connect(self.on_click_to_save)

        ##combo
        combo = QComboBox(self)
        combo.addItem("English")
        combo.addItem("Arabic")
        combo.addItem("Russian")
        combo.addItem("Chinese")
        combo.addItem("French")

        combo.move(20, 200)
        self.lbl.move(20, 200)

        combo.activated[str].connect(self.onActivated)

        self.show()

    def onActivated(self, text):
        self.lbl.setText(text)
        self.lbl.adjustSize()
        print(text)

    def start(self):
        if self.path_to_save != '':
            print(self.path_document)
            print(self.path_to_save)
            print(self.Checked)
            if self.Checked:
                stem = "yes"
            else:
                stem= "no"
            path_corpus = self.path_document.replace('\\','/')
            path_save = self.path_to_save.replace('\\', '/')
            print(path_corpus)
            result = Controller.init_path(path_corpus,path_save,stem)
            doc = result[0]
            term_not_stemming = result[1]
            term_stemming = result[2]
            minutes = result[3]
            seconds = result[4]

            print("start")
            QMessageBox.about(self, "Information", "Number of documents that have been indexed: " + doc + "\n"
                                                                                                           "Number of terms without stemming: " + term_not_stemming + "\n" +
                              "Number of terms stemming: " + term_stemming + "\n" + "Time: " + minutes+ " minutes"+ "\n" + "Time: " + seconds+ " seconds")
        else:
            QMessageBox.warning(self, "Something wrong", "No path entered or incorrect path entered")


    def clickBox(self, state):
        if state == QtCore.Qt.Checked:
            self.Checked = True
        else:
            self.Checked = False

    @pyqtSlot()
    def on_click_document(self):
        ex = App()
        self.path_document = ex.GetFileName()
        print("document " + self.path_document)
        self.textbox_documents.setPlaceholderText(self.path_document)
        self.show()

    @pyqtSlot()
    def on_click_to_save(self):
        ex = App()
        self.path_to_save = ex.GetFileName()
        print("save " + self.path_to_save)
        self.textbox_to_save.setPlaceholderText(self.path_to_save)
        self.show()

    def Reset(self):
        print("Reset")
        Controller.reset()

    # save posting in user path
    def LoadDictionery(self):
        if self.path_to_save != '':
            dictionary = Controller.load_dictionary(self.Checked)

        else:
            QMessageBox.warning(self, "Something wrong", "No path entered or incorrect path entered")

    # save posting in user path
    def DisplayDictionary(self): ##########################################dictionary
        if self.path_document != '':
            result = Controller.get_cach_dictionary()
            print(result)
            self.SW = SecondWindow()
            self.SW.show()
        else:
            QMessageBox.warning(self, "Something wrong", "No path entered or incorrect path entered")


class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Browse Path.com'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.fileName = ''
        self.initUI()

    def initUI(self):
        left = 10
        top = 10
        width = 640
        height = 480
        self.setWindowTitle(self.title)
        self.setGeometry(left, top, width, height)

        self.openFileNameDialog()
        # self.openFileNamesDialog()

        self.show()

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName = QFileDialog.getExistingDirectory(None, "QFileDialog.getOpenFileName()",
                                                  "All Files (*);;Python Files (*.py)", QFileDialog.ShowDirsOnly)
        if fileName:
            self. fileName = fileName

    def GetFileName(self):
        return self.fileName


class SecondWindow(QMainWindow):
    def __init__(self):
        super(SecondWindow, self).__init__()
        self.title = 'PyQt5 table - hadarrrrr.com'
        self.left = 300
        self.top = 300
        self.width = 700
        self.height = 500
        self.layout = QVBoxLayout()

        self.init_ui()


    def init_ui(self):
        QLabel("csslllllllllll", self)
        self.layout = QVBoxLayout()
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    Start = StartWindow()
    Start.resize(800, 600)
    Start.show()
    sys.exit(app.exec_())