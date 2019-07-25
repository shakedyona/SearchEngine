import json
import os

from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QPushButton, QApplication, QLabel, QButtonGroup, QAbstractButton
from PyQt5.QtWidgets import (QPushButton, QLineEdit, QLabel, QCheckBox, QComboBox)
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QMainWindow, QApplication, QWidget

import configparser
import json
import os
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox, QFileDialog,  QMainWindow, QApplication, QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout
from PyQt5.QtWidgets import (QPushButton, QLineEdit, QLabel, QCheckBox, QComboBox)
from PyQt5.QtCore import pyqtSlot
from PyQt5 import QtCore
import sys
import subprocess as sp

from Controller import Controller

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.memory = False
        self.have_other_win = False
        self.list_of_docs = []
        # path corpus
        self.path_document = ''
        self.textbox_documents = QLineEdit(self)
        # self.textbox_documents.insert("path")
        # self.textbox_documents.setText("set path")
        self.textbox_documents.setGeometry(QtCore.QRect(20,20,280,40))
        self.button_textbox_documents = QPushButton('Browse path of corpus', self)
        self.button_textbox_documents.setStyleSheet("font-size: 18px")
        self.button_textbox_documents.setGeometry(QtCore.QRect(350, 20, 250, 40))
        self.button_textbox_documents.clicked.connect(self.on_click_document)

        # path save
        self.path_to_save = ''
        self.textbox_to_save = QLineEdit(self)
        self.textbox_to_save.setGeometry(QtCore.QRect(20, 85, 280, 40))
        self.button_textbox_to_save = QPushButton('Browse path to save on', self)
        self.button_textbox_to_save.setStyleSheet("font-size: 18px")
        self.button_textbox_to_save.setGeometry(QtCore.QRect(350, 85, 250, 40))
        self.button_textbox_to_save.clicked.connect(self.on_click_to_save)

        # stemming
        self.Checked = False
        self.b = QCheckBox("stemming?", self)
        self.b.setGeometry(QtCore.QRect(20, 150, 250, 40))
        self.b.setStyleSheet("font-size: 18px")
        self.b.stateChanged.connect(self.clickBox)


        # Languages
        combo = QComboBox(self)
        combo.setGeometry(QtCore.QRect(20, 215, 250, 40))
        folder_name = r"Model\ReadFile"
        file_path = folder_name + "/" + 'languages.json'
        if os.path.exists(file_path):
            with open(file_path, 'r') as openfile:
                languages = json.load(openfile)
        for leng in languages:
            combo.addItem(str(leng))
        combo.activated[str].connect(self.onActivated)

        # path load query
        self.path_to_query = ''
        self.textbox_to_load_query = QLineEdit(self)
        self.textbox_to_load_query.setGeometry(QtCore.QRect(20, 280, 280, 40))
        self.button_textbox_to_load_query = QPushButton('Browse path of a query file', self)
        self.button_textbox_to_load_query.setStyleSheet("font-size: 18px")
        self.button_textbox_to_load_query.setGeometry(QtCore.QRect(350, 280, 250, 40))
        self.button_textbox_to_load_query.clicked.connect(self.on_click_to_load_query)
        self.button_textbox_file_query = QPushButton('Run queries', self)
        self.button_textbox_file_query.setEnabled(False)
        self.button_textbox_file_query.setStyleSheet("background-color: #22ca58 ; font-size: 25px")
        self.button_textbox_file_query.setGeometry(QtCore.QRect(20, 345, 580, 40))
        self.button_textbox_file_query.clicked.connect(self.on_click_to_run_queries)


        # text field query
        self.text_to_query = ''
        self.textbox_query = QLineEdit(self)
        self.textbox_query.insert("Enter a query...\n")
        self.textbox_query.setGeometry(QtCore.QRect(20, 410, 280, 40))
        self.button_textbox_text_query = QPushButton('Run query', self)
        self.button_textbox_text_query.setStyleSheet("background-color: #22ca58 ; font-size: 25px")
        self.button_textbox_text_query.setGeometry(QtCore.QRect(350, 410, 250, 40))
        self.button_textbox_text_query.clicked.connect(self.on_click_to_text_query)

        # semantics
        self.Checked_semantics = False
        self.semantics_box = QCheckBox("semantics?", self)
        self.semantics_box.setGeometry(QtCore.QRect(20, 470, 250, 40))
        self.semantics_box.setStyleSheet("font-size: 18px")
        self.semantics_box.stateChanged.connect(self.clickBox_semantics)

        # buttons

        self.button_start = QPushButton("Start",self)
        self.button_start.setGeometry(QtCore.QRect(620, 20, 580, 40))
        self.button_start.setStyleSheet("background-color: #22ca58 ; font-size: 25px")
        self.button_start.clicked.connect(self.start)

        self.button_reset = QPushButton("Reset",self)
        self.button_reset.setGeometry(QtCore.QRect(620, 85, 580, 40))
        self.button_reset.setStyleSheet("background-color: red ; font-size: 25px")
        self.button_reset.clicked.connect(self.Reset)

        self.button_Load_dictionary = QPushButton("Load the dictionary",self)
        self.button_Load_dictionary.setGeometry(QtCore.QRect(620, 150, 580, 40))
        self.button_Load_dictionary.setStyleSheet("background-color: #ffd05b ; font-size: 25px")
        self.button_Load_dictionary.clicked.connect(self.LoadDictionery)

        self.button_display_dictionary = QPushButton("Display dictionary",self)
        self.button_display_dictionary.setGeometry(QtCore.QRect(620, 215, 580, 40))
        self.button_display_dictionary.setStyleSheet("background-color: #ffd05b ; font-size: 25px")
        self.button_display_dictionary.clicked.connect(self.DisplayDictionary)

        self.button_select_cities = QPushButton("Select cities to filter results", self)
        self.button_select_cities.setGeometry(QtCore.QRect(620, 280, 580, 40))
        self.button_select_cities.setStyleSheet("background-color: #90dfaa ; font-size: 25px")
        self.button_select_cities.clicked.connect(self.open_cities_window)

        self.button_save_results_query = QPushButton("Save queries results", self)
        self.button_save_results_query.setGeometry(QtCore.QRect(620, 345, 580, 40))
        self.button_save_results_query.setStyleSheet("background-color: #90dfaa ; font-size: 25px")
        self.button_save_results_query.setEnabled(False)
        self.button_save_results_query.clicked.connect(self.save_results_query)

        self.button_save_results_query_one_query = QPushButton("Save query results", self)
        self.button_save_results_query_one_query.setGeometry(QtCore.QRect(620, 410, 580, 40))
        self.button_save_results_query_one_query.setStyleSheet("background-color: #90dfaa ; font-size: 25px")
        self.button_save_results_query_one_query.setEnabled(False)
        self.button_save_results_query_one_query.clicked.connect(self.save_results_query_one_query)

    def open_cities_window(self):
        if self.path_to_save != '' and self.path_document != '':
            print("open_cities_window")
            self.have_other_win = True
            self.SW = SecondWindow(self.path_to_save)
            self.SW.resize(1500, 900)
            self.SW.show()
        else:
            QMessageBox.warning(self, "Something wrong", "No path entered or incorrect path entered")

    # stemming
    def clickBox(self, state):
        if state == QtCore.Qt.Checked:
            self.Checked = True
            print("stem true")
        else:
            self.Checked = False
            print("stem false")

    # semantics
    def clickBox_semantics(self, state):
        if state == QtCore.Qt.Checked:
            self.Checked_semantics = True
            print("semantics true")
        else:
            self.Checked_semantics = False
            print("semantics false")


    # Languages
    def onActivated(self, text):
        print(text)

    # path corpus
    @pyqtSlot()
    def on_click_document(self):
        ex = App()
        self.path_document = ex.GetFileName()
        print("document " + self.path_document)
        self.textbox_documents.setPlaceholderText(self.path_document)

        self.show()

    # path save
    @pyqtSlot()
    def on_click_to_save(self):
        ex = App()
        self.path_to_save = ex.GetFileName()
        print("save " + self.path_to_save)
        self.textbox_to_save.setPlaceholderText(self.path_to_save)
        self.show()

    # path load query
    @pyqtSlot()
    def on_click_to_load_query(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self, "QFileDialog.getOpenFileNames()", "",
                                                "All Files (*);;Python Files (*.py)", options=options)
        if files:
            self.path_to_query = files[0]
            print("query " + self.path_to_query)
            self.textbox_to_load_query.setPlaceholderText(self.path_to_query)
            self.button_textbox_file_query.setEnabled(True)

        # ex = App()
        # self.path_to_query = ex.GetFileName()
        # print("query " + self.path_to_query)
        # self.textbox_to_load_query.setPlaceholderText(self.path_to_query)
        # self.button_textbox_file_query.setEnabled(True)
        # self.show()

    # run load queries
    @pyqtSlot()
    def on_click_to_run_queries(self):
        if self.path_to_save != '' and self.path_document!='' and self.path_to_query!='':
            print("on_click_to_run_queries",self.path_to_query)
            # print result
            if self.have_other_win:
                print("here")
                self.list_cities_selected = self.SW.get_cities()
                print(self.list_cities_selected)
                print("shaked")
            else:
                self.list_cities_selected = []
                print(self.list_cities_selected)
                print("no selected cities")

            if self.Checked:
                stem = "yes"
            else:
                stem = "no"
            print("semantics mode",self.Checked_semantics)
            total_time, self.list_of_docs = Controller.load_query_file(self.path_to_query,stem,self.path_document,self.path_to_save,self.list_cities_selected,self.Checked_semantics)
            print("in view: ",total_time,self.list_of_docs)
            self.button_save_results_query.setEnabled(True)
            self.button_save_results_query_one_query.setEnabled(False)
            print("open_results_window")
            self.TW = ThirdWindow(self.list_of_docs,stem,self.path_to_save,self.path_document)
            self.TW.resize(1900, 1000)
            self.TW.show()

        else:
            QMessageBox.warning(self, "Something wrong", "No path entered or incorrect path entered")




    # run text query
    @pyqtSlot()
    def on_click_to_text_query(self):
        if self.path_to_save != '' and self.path_document!='' and self.textbox_query.text()!="Enter a query...\n":
            self.text_to_query = self.textbox_query.text()
            print("text: " + self.text_to_query)

            # print result
            if self.have_other_win:
                print("here")
                self.list_cities_selected = self.SW.get_cities()
                print(self.list_cities_selected)
                print("shaked")
            else:
                self.list_cities_selected = []
                print(self.list_cities_selected)
                print("no selected cities")

            if self.Checked:
                stem = "yes"
            else:
                stem = "no"

            print("semantics mode",self.Checked_semantics)
            total_time, self.list_of_docs = Controller.enter_query_text(self.text_to_query,stem,self.path_document,self.path_to_save,self.list_cities_selected,self.Checked_semantics)
            print("in view: ",total_time,self.list_of_docs)
            self.button_save_results_query_one_query.setEnabled(True)
            self.button_save_results_query.setEnabled(False)
            print("open_results_window")
            self.TF = FourWindow(self.list_of_docs,stem,self.path_to_save,self.path_document)
            self.TF.resize(700, 900)
            self.TF.show()

        else:
            QMessageBox.warning(self, "Something wrong", "No path entered or incorrect path entered or Enter a query...")

        # number1 = 1
        # res1 = "file name 1"
        # number2 = 2
        # res2 = "file name 2"
        # QMessageBox.about(self, "Results", str(number1) + ") " + res1 + "\n"
        #                   + str(number2) + ") " + res2 + "\n")

    # display results queries
    def save_results_query(self):
        print("save results queries")
        path_folder = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        print(path_folder)
        Controller.save_result_from_load_query_to_file(self.list_of_docs,path_folder)

    # display results query
    def save_results_query_one_query(self):
        print("save results query")
        path_folder = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        print(path_folder)
        Controller.save_result_from_query_text_to_file(self.list_of_docs,path_folder)

    # # entity recognition
    # def entity_recognition(self):
    #     print("Entity Search")

    # start
    def start(self):
        if self.path_to_save != '' and self.path_document!='':
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
            self.memory = True
            self.button_select_cities.setEnabled(True)
            print("start")
            QMessageBox.about(self, "Information", "Number of documents that have been indexed: " + doc + "\n"
                                                                                                           "Number of terms without stemming: " + term_not_stemming + "\n" +
                              "Number of terms stemming: " + term_stemming + "\n" + "Time: " + minutes+ " minutes"+ "\n" + "Time: " + seconds+ " seconds")
        else:
            QMessageBox.warning(self, "Something wrong", "No path entered or incorrect path entered")

    # Load Dictionery
    def LoadDictionery(self):
        if self.path_to_save != '' and self.path_document!='':
            print("LoadDictionery")
            self.memory = True
            if self.Checked:
                stem = "yes"
            else:
                stem= "no"
            Controller.load_dictionary(stem,self.path_to_save)
            self.button_select_cities.setEnabled(True)

        else:
            QMessageBox.warning(self, "Something wrong", "No path entered or incorrect path entered")

    # Display Dictionary
    def DisplayDictionary(self):
        if self.path_to_save != '' and self.path_document!='':
            if self.Checked:
                stem = "yes"
            else:
                stem= "no"
            cach_dictionary = Controller.get_cach_dictionary(stem)
            try:
                zip_file_dic = open(self.path_to_save + "/dictionary_freq.txt", "w")

            except IOError:
                return "fail"

            for term, value in cach_dictionary.items():
                zip_file_dic.write(term + "-->" + str(value[0]) + '\n')
            zip_file_dic.close()
            print("finish")
            fileName = self.path_to_save + "/dictionary_freq.txt"
            programName = "notepad.exe"
            sp.Popen([programName, fileName])

        else:
            QMessageBox.warning(self, "Something wrong", "No path entered or incorrect path entered")

    # reset
    def Reset(self):
        print("Reset")
        if self.path_to_save != '' and self.path_document!='':
            if self.memory:
                print("Reset")
                self.memory = False
                self.button_select_cities.setEnabled(False)
                Controller.reset(self.path_to_save)
                print("finish reset controller")
                dic_path = self.path_to_save + '/' + "dictionary_freq.txt"
                os.remove(dic_path)
                print("finish reset")

        else:
            QMessageBox.warning(self, "Something wrong", "No path entered or incorrect path entered")



class App(QMainWindow):

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
    def __init__(self,save):
        super(SecondWindow, self).__init__()
        print("SecondWindow - into")
        # cities
        self.selected_label = QLabel('{}', self)
        self.selected_label.setGeometry(QtCore.QRect(20, 0, 1200, 40))

        self.check_dic = {}
        self.bool_dic = {}
        self.list_selected = set()
        print("SecondWindow - into2")
        file_path_city = save + "/json/" + 'dictionary_cities.json'
        print(file_path_city)
        if os.path.exists(file_path_city):
            with open(file_path_city, 'r') as openfile:
                cities = json.load(openfile)

        cities = sorted(cities)
        x = 40
        y = 20
        counter = 1
        self.bg = QButtonGroup()

        for city in cities:
            self.bool_dic[city] = counter
            self.check_dic[city] = QCheckBox(str(city), self)
            self.check_dic[city].setGeometry(QtCore.QRect(y, x, 130, 40))
            self.bg.addButton(self.check_dic[city], counter)
            x = x + 25
            if counter % 30 == 0:
                y = y + 130
                x = 40
            counter = counter + 1
        print(self.bool_dic)
        self.bg.buttonClicked[QAbstractButton].connect(self.clickBox_city)
        print(self.list_selected)

        self.button_done = QPushButton("Save my selections", self)
        self.button_done.setGeometry(QtCore.QRect(20, 820, 1460, 40))
        self.button_done.setStyleSheet("background-color: #22ca58 ; font-size: 25px")
        self.button_done.clicked.connect(self.done)

    def clickBox_city(self, state):
        print(self.list_selected)
        if state.isChecked():
            print(state.text() + " is selected")
            if state.text() in self.list_selected:
                self.list_selected.remove(state.text())
            else:
                self.list_selected.add(state.text())
            print(self.list_selected)
        if self.list_selected:
            self.selected_label.setText(str(self.list_selected))
        else:
            self.selected_label.setText('{}')

    def done(self):
        print("done")
        self.button_done.setText("Saved !")
        print(self.list_selected)

    def get_cities(self):
        return self.list_selected

class ThirdWindow(QMainWindow):
    def __init__(self,list_result,stemm,save,corpus):
        super(ThirdWindow, self).__init__()
        print("ThirdWindow")
        self.result_label = QLabel('Results: \nClick the document that you want to display the dominant entities ...', self)
        self.result_label.setStyleSheet("font-size: 15px")
        self.result_label.setGeometry(QtCore.QRect(5, 0, 1200, 40))
        self.entity_label = QLabel('', self)
        self.most_dominat_entities = []
        self.label_docs = {}
        self.button_docs = {}
        self.stemm_send = stemm
        self.save_folder = save
        self.corpus = corpus
        x = 40
        y = 10
        counter = 1
        self.button_g = QButtonGroup()

        #for doc in list_result:
        #for doc in range(1,51):
        for query_docs in list_result:
            query_id = query_docs[0]
            results_set = set(query_docs[1])
            for doc in results_set:
                self.button_docs[doc] = QPushButton(str(query_id+": "+doc), self)
                self.button_docs[doc].setStyleSheet("font-size: 10px")
                self.button_docs[doc].setGeometry(QtCore.QRect(y, x, 110, 19))
                self.button_g.addButton(self.button_docs[doc], counter)
                x = x + 19
                if counter % 50 == 0:
                    y = y + 110
                    x = 40
                counter = counter + 1
        self.button_g.buttonClicked[QAbstractButton].connect(self.click_entity)


    def click_entity(self,button_clicked):
        print("click_entity")
        print(button_clicked.text() + " is selected")
        self.list_entity = Controller.entity_search(button_clicked.text(),self.stemm_send,self.save_folder,self.corpus)
        entities = ""
        print("here - click entity")
        for entity,rank in self.list_entity.items():
            entities = entities + entity+" --> "+str("{:.2f}".format(rank))+'\n'
        self.entity_label.setText('The most dominant entities of :\n ' + button_clicked.text() + ' :\n' + str(entities))
        self.entity_label.setStyleSheet("font-size: 13px")
        self.entity_label.setGeometry(QtCore.QRect(1700,0, 200, 500))

class FourWindow(QMainWindow):
    def __init__(self,list_result,stemm,save,corpus):
        super(FourWindow, self).__init__()
        print("FourWindow")
        self.result_label = QLabel('Results: \nClick the document that you want to display the dominant entities ...', self)
        self.result_label.setStyleSheet("font-size: 20px")
        self.result_label.setGeometry(QtCore.QRect(20, 20, 1200, 60))
        self.entity_label = QLabel('', self)
        self.most_dominat_entities = []
        self.label_docs = {}
        self.button_docs = {}
        self.stemm_send = stemm
        self.save_folder = save
        self.corpus = corpus
        x = 80
        y = 20
        counter = 1
        self.button_g = QButtonGroup()

        #for doc in list_result:
        #for doc in range(1,51):
        for doc in list_result:
            self.button_docs[doc] = QPushButton(str(doc), self)
            self.button_docs[doc].setGeometry(QtCore.QRect(y, x, 130, 60))
            self.button_g.addButton(self.button_docs[doc], counter)
            x = x + 60
            if counter % 10 == 0:
                y = y + 130
                x = 80
            counter = counter + 1
        self.button_g.buttonClicked[QAbstractButton].connect(self.click_entity)


    def click_entity(self,button_clicked):
        print("click_entity")
        print(button_clicked.text() + " is selected")
        self.list_entity = Controller.entity_search("000: "+button_clicked.text(),self.stemm_send,self.save_folder,self.corpus)
        entities = ""
        for entity,rank in self.list_entity.items():
            entities = entities + entity+" --> "+str("{:.2f}".format(rank))+'\n'
        self.entity_label.setText('The most dominant entities of :\n ' + button_clicked.text() + ' :\n' + str(entities))
        self.entity_label.setStyleSheet("font-size: 13px")
        self.entity_label.setGeometry(QtCore.QRect(20,700, 1200, 150))

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    MW = MainWindow()
    MW.resize(1220, 700)
    MW.show()
    sys.exit(app.exec_())