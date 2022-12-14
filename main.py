# Тест скорости печати на основе PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCharFormat, QColor, QPen, QTextCursor, QIcon, QPalette, QFont
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QAction, QFileDialog, QInputDialog, QProgressBar
from datetime import date
from pyqtgraph import PlotWidget
import sqlite3
import sys


class MainWidget(QMainWindow):  # Основное окно приложения
    def __init__(self, parent=None):
        super(MainWidget, self).__init__(parent)
        self.setupUi(self)

        self.bright_palette = app.palette()

        self.scroll_k = 0
        self.filepath, self.sample_text, self.theme, self.time = '', '', 0, 1
        self.minutes, self.seconds = 0, 0
        self.loadSettings()

        self.startBtn.clicked.connect(self.execute)
        self.statsBtn.clicked.connect(self.openStats)

        self.mistakes = 0
        self.speed = 0
        self.accuracy = 100
        self.mistake_list = []

        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.onTimeout)

        self.index = 0
        self.checker = QtCore.QTimer()
        self.checker.setInterval(10)
        self.checker.timeout.connect(self.checkMistakes)

        self.format = QTextCharFormat()
        self.format.setTextOutline(QPen(QColor("red")))

        bar = self.menuBar()
        bar.hide()

        self.menu = bar.addMenu("Menu")

        theme = self.menu.addMenu("Выбрать тему")
        theme.addAction("светлая")
        theme.addAction("темная")

        theme.triggered.connect(self.changeTheme)

        settings = QAction("Настройки", self)
        settings.triggered.connect(self.openSettings)
        self.menu.addAction(settings)

        openFile = QAction("Открыть файл...", self)
        openFile.triggered.connect(self.chooseFile)
        self.menu.addAction(openFile)

        quit = QAction("Выйти", self)
        quit.setShortcut("Ctrl+Q")
        quit.triggered.connect(app.quit)
        self.menu.addAction(quit)

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        self.setWindowIcon(QtGui.QIcon('files/icon.png'))
        MainWindow.resize(724, 804)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setContentsMargins(10, 0, 10, -1)
        self.gridLayout.setHorizontalSpacing(20)
        self.gridLayout.setVerticalSpacing(5)
        self.gridLayout.setObjectName("gridLayout")
        self.plainEdit = QtWidgets.QPlainTextEdit(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semilight")
        font.setPointSize(16)
        self.plainEdit.setFont(font)
        self.plainEdit.setPlainText("")
        self.plainEdit.setObjectName("plainEdit")
        self.gridLayout.addWidget(self.plainEdit, 3, 0, 1, 3)
        self.statsCB = QtWidgets.QCheckBox(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semilight")
        font.setPointSize(10)
        self.statsCB.setFont(font)
        self.statsCB.setObjectName("statsCB")
        self.gridLayout.addWidget(self.statsCB, 4, 0, 1, 1)
        self.speed_lab = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Nirmala UI Semilight")
        font.setPointSize(10)
        self.speed_lab.setFont(font)
        self.speed_lab.setObjectName("speed_lab")
        self.gridLayout.addWidget(self.speed_lab, 1, 1, 1, 1)
        self.accuracy_lab = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semilight")
        font.setPointSize(10)
        self.accuracy_lab.setFont(font)
        self.accuracy_lab.setObjectName("accuracy_lab")
        self.gridLayout.addWidget(self.accuracy_lab, 1, 2, 1, 1)
        self.time_pb = QProgressBar(self)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semilight")
        font.setPointSize(10)
        # self.time_lab.setFont(font)
        self.time_pb.setObjectName("time_pb")
        self.time_pb.setGeometry(30, 40, 80, 25)
        self.gridLayout.addWidget(self.time_pb, 1, 0, 1, 1)
        self.time_pb.setValue(100)
        self.statsBtn = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.statsBtn.sizePolicy().hasHeightForWidth())
        self.statsBtn.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semilight")
        font.setPointSize(10)
        self.statsBtn.setFont(font)
        self.statsBtn.setObjectName("statsBtn")
        self.gridLayout.addWidget(self.statsBtn, 5, 0, 1, 1)
        self.plainSample = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.plainEdit.setReadOnly(True)
        self.plainSample.setEnabled(False)
        font1 = QtGui.QFont()
        font1.setFamily("Segoe UI Semibold")
        font1.setPointSize(14)
        font1.setBold(False)
        font1.setStyleHint(QFont.TypeWriter)
        font1.setWeight(75)
        self.plainSample.setFont(font1)
        self.plainSample.setMouseTracking(False)
        self.plainSample.setAutoFillBackground(False)
        self.plainSample.setObjectName("plainSample")
        self.gridLayout.addWidget(self.plainSample, 2, 0, 1, 3)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semilight")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 1, 1, 1)
        self.label_1 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semilight")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_1.setFont(font)
        self.label_1.setObjectName("label_1")
        self.gridLayout.addWidget(self.label_1, 0, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semilight")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 2, 1, 1)
        self.startBtn = QtWidgets.QPushButton(self.centralwidget)
        self.startBtn.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.startBtn.sizePolicy().hasHeightForWidth())
        self.startBtn.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semilight")
        font.setPointSize(20)
        self.startBtn.setFont(font)
        self.startBtn.setObjectName("startBtn")
        self.gridLayout.addWidget(self.startBtn, 4, 1, 2, 2)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 724, 19))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "hypetype300"))
        self.statsCB.setText(_translate("MainWindow", "Записывать статистику"))
        self.speed_lab.setText(_translate("MainWindow", "0 символов / мин."))
        self.accuracy_lab.setText(_translate("MainWindow", "100%"))
        self.statsBtn.setText(_translate("MainWindow", "Смотреть статистику"))
        self.plainSample.setPlainText(_translate("MainWindow", "Пример текста"))
        self.label_2.setText(_translate("MainWindow", "Скорость"))
        self.label_1.setText(_translate("MainWindow", f'Время'))
        self.label_3.setText(_translate("MainWindow", "Точность"))
        self.startBtn.setText(_translate("MainWindow", "Начать"))

    def execute(self):  # Метод запуска/остановки теста
        self.plainEdit.setPlainText('')
        if self.startBtn.text() == 'Начать':

            self.minutes, self.seconds = self.default_time // 60, self.default_time % 60 \
                if (self.default_time % 60) >= 10 else '0' + str(self.default_time % 60)

            self.label_1.setText(f'Время   {self.minutes}:{self.seconds}')
            self.startBtn.setText('Остановить')

            self.statsBtn.setEnabled(False)
            self.statsCB.setEnabled(False)

            try:
                if self.text is not None:
                    self.plainSample.setPlainText(self.text)
                else:
                    self.plainSample.setPlainText(self.default_text)
            except AttributeError:
                self.plainSample.setPlainText(self.default_text)

            self.plainEdit.setReadOnly(False)

            self.checker.start(10)
            self.timer.start(1000)

        else:
            self.scroll_k = 0

            cursor = self.plainSample.textCursor()
            cursor.select(QtGui.QTextCursor.Document)
            cursor.setCharFormat(QtGui.QTextCharFormat())
            cursor.clearSelection()
            self.plainSample.setTextCursor(cursor)

            self.label_1.setText(f'Время')
            self.text = None

            self.startBtn.setText('Начать')
            self.statsBtn.setEnabled(True)
            self.statsCB.setEnabled(True)

            self.plainSample.setPlainText(self.sample_text)
            self.plainEdit.setReadOnly(True)

            self.time = self.default_time
            self.speed_lab.setText("0 символов / мин.")
            self.accuracy_lab.setText("100%")
            self.time_pb.setValue(100)

            self.mistakes = 0
            self.speed = 0
            self.accuracy = 100
            self.mistake_list = []

            self.checker.stop()
            self.timer.stop()

    def onTimeout(self):  # Метод для обновления данных во время теста
        self.time -= 1

        if self.time == self.default_time - 1:
            for _ in range(11):
                self.plainSample.moveCursor(QtGui.QTextCursor.Down)

        if len(self.plainEdit.toPlainText()) >= 720 + self.scroll_k * 57:
            self.plainSample.moveCursor(QtGui.QTextCursor.Down)
            self.scroll_k += 1

        self.minutes, self.seconds = self.time // 60, self.time % 60 if (self.time % 60) >= 10 else '0' + str(
            self.time % 60)
        self.label_1.setText(f'Время   {self.minutes}:{self.seconds}')

        self.time_pb.setValue(int(self.time / self.default_time * 100))
        if self.time == 0:
            self.checker.stop()
            self.timer.stop()

            msg = QMessageBox(self)
            msg.setWindowIcon(QIcon("files/icon.png"))
            msg.setWindowTitle("Результат")
            msg.setIcon(QMessageBox.Information)
            msg.setText("Вы завершили тест, вот ваши результаты: ")

            if self.statsCB.isChecked():
                if self.accuracy > 50:
                    self.makeRecord()
                    db_result = "\n\nЗапись статистики успешно выполнена."
                else:
                    db_result = "\n\nЗапись статистики не была выполнена, так как ваша точность слишком низкая."
            else:
                db_result = ""

            msg.setInformativeText(f"Скорость: {self.speed} символов в минуту\nТочность: {self.accuracy}%{db_result}")
            buttonAceptar = msg.addButton("Ok", QMessageBox.AcceptRole)

            msg.exec_()
            self.execute()

    def checkMistakes(self):  # Метод для проверки ошибок и их выделения цветом
        self.accuracy_lab.setText(f'{self.accuracy}%')
        self.speed_lab.setText(f'{self.speed} символов / мин.')

        sym_number = len(str(self.plainEdit.toPlainText())) - 1
        symList = self.plainEdit.toPlainText()

        self.index = sym_number

        for _ in range(len(symList[self.index:])):
            cursor = self.plainSample.textCursor()
            cursor.setPosition(self.index)
            ww = cursor.movePosition(QTextCursor.Right, 1)
            self.format.setTextOutline(QPen(QColor("green")))
            cursor.mergeCharFormat(self.format)

            if self.plainEdit.toPlainText() != self.plainSample.toPlainText()[:sym_number + 1]:
                self.format.setTextOutline(QPen(QColor("red")))
                cursor.mergeCharFormat(self.format)
                if sym_number not in self.mistake_list:
                    self.mistake_list.append(sym_number)
                    self.mistakes += 1
            self.index += 1

        self.speed = round((sym_number + 1) / ((self.default_time - self.time) / 60), 1) \
            if self.time != self.default_time else 0
        self.accuracy = int(100 - (self.mistakes / (sym_number + 1) * 100)) if sym_number + 1 != 0 else 100

    def openStats(self):  # Метод открывает окно статистики
        dialog = StatsWidget(self)
        dialog.show()

    def openSettings(self):  # Метод открывает окно настроек
        if self.startBtn.text() == 'Остановить':
            return None

        dialog = SettingsWidget(self)
        dialog.show()

    def makeRecord(self):  # Метод для записи результата теста в базу данных
        conn = sqlite3.connect('files/database.sqlite')
        c = conn.cursor()

        c.execute("""CREATE TABLE IF NOT EXISTS stats (
            id       INTEGER PRIMARY KEY AUTOINCREMENT
                             NOT NULL
                             UNIQUE,
            speed    DOUBLE  NOT NULL,
            accuracy INTEGER NOT NULL,
            date     INTEGER NOT NULL
        );
        """)

        today = date.today()
        const = date(2000, 1, 1)
        day = (today - const).days

        len_res = c.execute('''select id from stats''')
        num = len(list(len_res)) + 1

        c.execute(f'''insert into stats values ({num}, {self.speed}, {self.accuracy}, {day})''')

        conn.commit()
        conn.close()

    def contextMenuEvent(self, event):  # Метод для вызова контекстного меню
        result = self.menu.exec_(self.mapToGlobal(event.pos()))

    def changeTheme(self, action):  # Метод для смены оформления приложения
        theme = action.text()
        if theme == 'светлая':
            app.setPalette(self.bright_palette)
            app.setStyleSheet("")
        else:
            dark_palette = QPalette()

            dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.WindowText, Qt.white)
            dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
            dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
            dark_palette.setColor(QPalette.ToolTipText, Qt.white)
            dark_palette.setColor(QPalette.Text, Qt.white)
            dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ButtonText, Qt.white)
            dark_palette.setColor(QPalette.BrightText, Qt.red)
            dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
            dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            dark_palette.setColor(QPalette.HighlightedText, Qt.black)

            app.setPalette(dark_palette)

            app.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")

    def chooseFile(self):  # Метод для выбора кастомного текста из файла для теста
        if self.startBtn.text() == 'Остановить':
            return None

        filepath = QFileDialog.getOpenFileName(self, 'Выбрать файл', '', 'Текстовый файл (*.txt);;Все файлы (*)')[0]

        filename = filepath.split("/")[-1]

        try:
            test_file = open(filepath, "r", encoding="utf-8").read()
        except FileNotFoundError:
            return None

        test_length = len(test_file)

        length, ok_pressed = QInputDialog.getInt(
            self, "Введите длину текста", f"Выбранный файл - {filename}",
            test_length // 2, 1, test_length, 10)

        self.text = test_file[:length].replace('\n', '')
        if ok_pressed:
            self.execute()

    def loadSettings(self):  # Метод, подгружающий настройки из базы данных
        conn = sqlite3.connect('files/database.sqlite')
        c = conn.cursor()

        c.execute("""CREATE TABLE IF NOT EXISTS settings (
            id         INTEGER PRIMARY KEY AUTOINCREMENT
                               NOT NULL
                               UNIQUE,
            filename   STRING  NOT NULL,
            time       INTEGER NOT NULL,
            theme      BOOLEAN NOT NULL,
            sampletext STRING  NOT NULL
        );""")

        if len(list(c.execute("""select * from settings"""))) == 0:
            c.execute(f'''insert into settings values (1, "files/samples.txt", 60, 0, "Пример текста")''')

        res = list(c.execute("""select * from settings"""))
        self.filepath = res[0][1]
        self.time = res[0][2]
        self.theme = res[0][3]

        if self.theme == 0:
            app.setPalette(self.bright_palette)
            app.setStyleSheet("")
        else:
            dark_palette = QPalette()

            dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.WindowText, Qt.white)
            dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
            dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
            dark_palette.setColor(QPalette.ToolTipText, Qt.white)
            dark_palette.setColor(QPalette.Text, Qt.white)
            dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ButtonText, Qt.white)
            dark_palette.setColor(QPalette.BrightText, Qt.red)
            dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
            dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            dark_palette.setColor(QPalette.HighlightedText, Qt.black)

            app.setPalette(dark_palette)

            app.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")

        self.sample_text = res[0][4]
        self.plainSample.setPlainText(self.sample_text)

        self.default_time = self.time
        self.minutes, self.seconds = self.default_time // 60, self.default_time % 60 \
            if (self.default_time % 60) >= 10 else '0' + str(self.default_time % 60)

        with open(self.filepath, "r", encoding="utf-8") as text:
            self.default_text = text.read().replace('\n', '')

        conn.commit()
        conn.close()


class StatsWidget(QMainWindow):  # Окно статистики

    def __init__(self, parent=None):
        self.bright_palette = app.palette()
        super(StatsWidget, self).__init__(parent)
        self.setupUi(self)

        self.comboBox.addItems(["За последние 7 дней", "За последние 30 дней", "За все время"])
        self.comboBox.activated.connect(self.showStats)

        self.speedCB.toggled.connect(self.showStats)
        self.accuracyCB.toggled.connect(self.showStats)

        bar = self.menuBar()
        bar.hide()

        self.menu = bar.addMenu("Menu")

        theme = self.menu.addMenu("Выбрать тему")
        theme.addAction("светлая")
        theme.addAction("темная")

        theme.triggered.connect(self.changeStatsTheme)

        quit = QAction("Выйти", self)
        quit.setShortcut("Ctrl+Q")
        quit.triggered.connect(self.close)
        self.menu.addAction(quit)

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        self.setWindowIcon(QtGui.QIcon('files/icon.png'))
        MainWindow.resize(752, 466)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setContentsMargins(10, 5, 10, -1)
        self.gridLayout.setVerticalSpacing(15)
        self.gridLayout.setObjectName("gridLayout")
        self.speedCB = QtWidgets.QRadioButton(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semilight")
        font.setPointSize(12)
        self.speedCB.setFont(font)
        self.speedCB.setObjectName("speedCB")
        self.gridLayout.addWidget(self.speedCB, 0, 0, 1, 1)
        self.accuracyCB = QtWidgets.QRadioButton(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semilight")
        font.setPointSize(12)
        self.accuracyCB.setFont(font)
        self.accuracyCB.setObjectName("accuracyCB")
        self.gridLayout.addWidget(self.accuracyCB, 0, 1, 1, 1)
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semilight")
        font.setPointSize(12)
        self.comboBox.setFont(font)
        self.comboBox.setEditable(False)
        self.comboBox.setCurrentText("")
        self.comboBox.setObjectName("comboBox")
        self.gridLayout.addWidget(self.comboBox, 0, 2, 1, 1)
        self.graphicsView = PlotWidget(self.centralwidget)
        self.graphicsView.setObjectName("graphicsView")
        self.gridLayout.addWidget(self.graphicsView, 1, 0, 1, 3)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 752, 19))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.plot = PlotWidget.getPlotItem(self.graphicsView)
        self.plot.setMenuEnabled(False)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Статистика"))
        self.speedCB.setText(_translate("MainWindow", "Скорость"))
        self.accuracyCB.setText(_translate("MainWindow", "Точность"))

    def showStats(self):  # Метод для отображения графиков
        self.graphicsView.clear()

        conn = sqlite3.connect('files/database.sqlite')
        c = conn.cursor()

        c.execute("""CREATE TABLE IF NOT EXISTS stats (
                    id       INTEGER PRIMARY KEY AUTOINCREMENT
                                     NOT NULL
                                     UNIQUE,
                    speed    DOUBLE  NOT NULL,
                    accuracy INTEGER NOT NULL,
                    date     INTEGER NOT NULL
                );
                """)

        conn.commit()

        today = date.today()
        const = date(2000, 1, 1)
        day = (today - const).days

        if self.comboBox.currentText() == "За последние 7 дней":
            result_speed = c.execute(f'''select speed from stats where date >= {day - 6}''').fetchall()
            result_accuracy = c.execute(f'''select accuracy from stats where date >= {day - 6}''').fetchall()
        elif self.comboBox.currentText() == "За последние 30 дней":
            result_speed = c.execute(f'''select speed from stats where date >= {day - 29}''').fetchall()
            result_accuracy = c.execute(f'''select accuracy from stats where date >= {day - 29}''').fetchall()
        else:
            result_speed = c.execute(f'''select speed from stats''').fetchall()
            result_accuracy = c.execute(f'''select accuracy from stats''').fetchall()

        y_speed = [i[0] for i in result_speed]
        y_accuracy = [i[0] for i in result_accuracy]
        xs = [i for i in range(len(y_speed))]

        if self.speedCB.isChecked():
            self.graphicsView.plot(xs, y_speed, pen='r')
        if self.accuracyCB.isChecked():
            self.graphicsView.plot(xs, y_accuracy, pen='b')

        conn.close()

    def contextMenuEvent(self, event):  # Метод для вызова контектсного меню
        result = self.menu.exec_(self.mapToGlobal(event.pos()))

    def changeStatsTheme(self, action):  # Метод для смены оформления приложения
        theme = action.text()
        if theme == 'светлая':
            MainWidget.changeTheme(self, QAction("светлая"))  # Вызов к прошлому классу
            # во избежание написания такого же кода второй раз
        else:
            MainWidget.changeTheme(self, QAction("темная"))


class SettingsWidget(QMainWindow):  # Окно настроек

    def __init__(self, parent=None):
        super(SettingsWidget, self).__init__(parent)
        self.setupUi(self)

        self.filepath, self.time, self.theme, self.sample_text = None, None, None, None
        self.themeCB.addItems(["Светлая тема", "Темная тема"])

        self.fileButton.clicked.connect(self.chooseFile)
        self.pushButton_2.clicked.connect(self.commitToDB)
        self.pushButton.clicked.connect(self.close)
        self.filenameLine.setReadOnly(True)

        self.loadSettings()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(506, 372)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(506, 372))
        MainWindow.setMaximumSize(QtCore.QSize(506, 372))
        font = QtGui.QFont()
        font.setPointSize(8)
        MainWindow.setFont(font)
        MainWindow.setToolTip("")
        MainWindow.setAnimated(True)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setHorizontalSpacing(10)
        self.gridLayout.setVerticalSpacing(50)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semilight")
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semilight")
        font.setPointSize(12)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 6, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semilight")
        font.setPointSize(12)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)
        self.filenameLine = QtWidgets.QLineEdit(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semilight")
        font.setPointSize(10)
        self.filenameLine.setFont(font)
        self.filenameLine.setObjectName("filenameLine")
        self.gridLayout.addWidget(self.filenameLine, 0, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semilight")
        font.setPointSize(12)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 4, 0, 1, 1)
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 7, 2, 1, 1)
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 7, 1, 1, 1)
        self.timel = QtWidgets.QSpinBox(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semilight")
        font.setPointSize(10)
        self.timel.setFont(font)
        self.timel.setAccelerated(True)
        self.timel.setMinimum(30)
        self.timel.setMaximum(600)
        self.timel.setSingleStep(5)
        self.timel.setProperty("value", 60)
        self.timel.setObjectName("time")
        self.gridLayout.addWidget(self.timel, 3, 1, 1, 2)
        self.themeCB = QtWidgets.QComboBox(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semilight")
        font.setPointSize(10)
        self.themeCB.setFont(font)
        self.themeCB.setCurrentText("")
        self.themeCB.setObjectName("themeCB")
        self.gridLayout.addWidget(self.themeCB, 4, 1, 1, 2)
        self.sample = QtWidgets.QLineEdit(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semilight")
        font.setPointSize(10)
        self.sample.setFont(font)
        self.sample.setObjectName("sample")
        self.gridLayout.addWidget(self.sample, 6, 1, 1, 2)
        self.fileButton = QtWidgets.QToolButton(self.centralwidget)
        self.fileButton.setObjectName("fileButton")
        self.gridLayout.addWidget(self.fileButton, 0, 2, 1, 2)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 506, 19))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Настройки"))
        self.label.setText(_translate("MainWindow", "Файл текста теста по умолчанию"))
        self.label_2.setText(_translate("MainWindow", "Текст примера"))
        self.label_3.setText(_translate("MainWindow", "Время на тест, в секундах"))
        self.filenameLine.setText(_translate("MainWindow", "files/samples.txt"))
        self.label_4.setText(_translate("MainWindow", "Оформление приложения"))
        self.pushButton.setText(_translate("MainWindow", "Ок"))
        self.pushButton_2.setText(_translate("MainWindow", "Применить"))
        self.sample.setText(_translate("MainWindow", "Пример текста"))
        self.fileButton.setText(_translate("MainWindow", "..."))

    def loadSettings(self):  # Метод для подгрузки настроек
        conn = sqlite3.connect('files/database.sqlite')
        c = conn.cursor()

        res = list(c.execute("""select * from settings"""))

        self.filepath = res[0][1]
        self.time = res[0][2]
        self.theme = res[0][3]
        self.sample_text = res[0][4]

        self.filenameLine.setText(self.filepath)
        self.timel.setValue(self.time)
        self.sample.setText(self.sample_text)

        self.themeCB.setCurrentIndex(self.theme)

    def chooseFile(self):  # Метод для выбора файла с текстом теста по умолчанию
        filepath = QFileDialog.getOpenFileName(self, 'Выбрать файл', '', 'Текстовый файл (*.txt);;Все файлы (*)')[0]

        try:
            open(filepath, "r", encoding="utf-8").read()
        except FileNotFoundError:
            return None

        self.filenameLine.setText(filepath)

    def commitToDB(self):  # Метод для отправки настроек в базу данных
        conn = sqlite3.connect('files/database.sqlite')
        c = conn.cursor()

        c.execute(f"""UPDATE settings SET filename = '{self.filenameLine.text()}'""")
        c.execute(f"""UPDATE settings SET time = {self.timel.value()}""")
        c.execute(f"""UPDATE settings SET theme = {self.themeCB.currentIndex()}""")
        c.execute(f"""UPDATE settings SET sampletext = '{self.sample.text()}'""")

        conn.commit()

        MainWidget.loadSettings(ex)

        conn.close()


if __name__ == "__main__":  # Запуск программы
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    ex = MainWidget()
    ex.show()
    sys.exit(app.exec_())
