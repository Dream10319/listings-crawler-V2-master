import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QComboBox, QMessageBox
from PyQt5.QtCore import Qt
from scrape.ctcassociates import *
from scrape.adsprecise import *
from scrape.adstransitions import *
from scrape.dentaltrans import *
from scrape.fryepracticesales import *
from scrape.menlotransitions import *
from scrape.dgtransitions import *
from scrape.knutzenmcvaygroup import *
from scrape.mydentalbroker import *
from scrape.professionaltransition import *
from scrape.ddsmatch import *
from scrape.omni import *
from scrape.westernpracticesales import *
from scrape.henryschein import *
from lib.db import *
from dotenv import load_dotenv
load_dotenv()

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.thread = None
        self.db_thread = None

    def initUI(self):
        self.setWindowTitle('Dental Data Scraping')
        self.setFixedSize(300, 100)
        layout = QVBoxLayout()

        self.combo_box = QComboBox()
        
        #----------- Websites --------------------
        self.combo_box.addItem("ctc-associates.com")
        self.combo_box.addItem("adsprecise.com")
        # self.combo_box.addItem("adstransitions.com")
        self.combo_box.addItem("dentaltrans.com")
        # self.combo_box.addItem("fryepracticesales.com")
        self.combo_box.addItem("menlotransitions.com")
        self.combo_box.addItem("dgtransitions.com")
        # self.combo_box.addItem("knutzenmcvaygroup.com") // not available
        self.combo_box.addItem("mydentalbroker.com")
        self.combo_box.addItem("professionaltransition.com")
        self.combo_box.addItem("ddsmatch.com")
        self.combo_box.addItem("omni-pg.com")
        self.combo_box.addItem("westernpracticesales.com")
        self.combo_box.addItem("dentalpracticetransitions.henryschein.com")
        
        combo_font = self.combo_box.font()
        combo_font.setPointSize(15)
        self.combo_box.setFont(combo_font)
        layout.addWidget(self.combo_box)

        self.scrape_btn = QPushButton('Scrape')
        btn_font = self.scrape_btn.font()
        btn_font.setPointSize(15)
        self.scrape_btn.setFixedHeight(30)
        self.scrape_btn.setFont(btn_font)
        self.scrape_btn.clicked.connect(self.scrape_btn_click)
        
        layout.addWidget(self.scrape_btn)

        self.setLayout(layout)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint) 
        self.show()

    def scrape_btn_click(self):
        origin = self.combo_box.currentText()
        self.scrape_btn.setText('Scraping...')
        self.scrape_btn.setDisabled(True)

        if origin == 'ctc-associates.com':
            self.thread = ctcScrape_thread()
            self.thread.finished.connect(self.handle_scraping_result)
            self.thread.start()
        elif origin == 'adsprecise.com':
            self.thread = adsScrape_thread()
            self.thread.finished.connect(self.handle_scraping_result)
            self.thread.start()
        elif origin == 'adstransitions.com':
            self.thread = adstransitionScrape_thread()
            self.thread.finished.connect(self.handle_scraping_result)
            self.thread.start()
        elif origin == 'dentaltrans.com':
            self.thread = dentaltranScrape_thread()
            self.thread.finished.connect(self.handle_scraping_result)
            self.thread.start()
        elif origin == "fryepracticesales.com":
            self.thread = fryepracticesalesScrape_thread()
            self.thread.finished.connect(self.handle_scraping_result)
            self.thread.start()
        elif origin == "menlotransitions.com":
            self.thread = menlotransactionScrape_thread()
            self.thread.finished.connect(self.handle_scraping_result)
            self.thread.start()
        elif origin == "dgtransitions.com":
            self.thread = dgtransitionScrape_thread()
            self.thread.finished.connect(self.handle_scraping_result)
            self.thread.start()
        elif origin == "knutzenmcvaygroup.com":
            self.thread = knutzenmcvaygroupScrape_thread()
            self.thread.finished.connect(self.handle_scraping_result)
            self.thread.start()
        elif origin == "mydentalbroker.com":
            self.thread = mydentalbrokerScrape_thread()
            self.thread.finished.connect(self.handle_scraping_result)
            self.thread.start()
        elif origin == 'professionaltransition.com':
            self.thread = professionalTransitionScrape_thread()
            self.thread.finished.connect(self.handle_scraping_result)
            self.thread.start()
        elif origin == "ddsmatch.com":
            self.thread = ddsmatchScrape_thread()
            self.thread.finished.connect(self.handle_scraping_result)
            self.thread.start()
        elif origin == "omni-pg.com":
            self.thread = omniScrape_thread()
            self.thread.finished.connect(self.handle_scraping_result)
            self.thread.start()
        elif origin == "westernpracticesales.com":
            self.thread = westernPracticeSalesScrape_thread()
            self.thread.finished.connect(self.handle_scraping_result)
            self.thread.start()
        elif origin == "dentalpracticetransitions.henryschein.com":
            self.thread = henryscheinScrape_thread()
            self.thread.finished.connect(self.handle_scraping_result)
            self.thread.start()

    def handle_scraping_result(self, result):
        # Handle the returned value here
        self.scrape_btn.setText('Saving...')
        self.db_thread = save_data_thread(result)
        self.db_thread.finished.connect(self.save_result_db)
        self.db_thread.start()

    def save_result_db(self):
        self.scrape_btn.setText('Scrape')
        self.scrape_btn.setDisabled(False)
        open_dialog("Success", "Data has been successfully scraped.")

def open_dialog(title, message):
    msg_box = QMessageBox()
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    msg_box.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = MyWidget()
    widget.show()
    sys.exit(app.exec_())