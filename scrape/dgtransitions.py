import mechanicalsoup
from PyQt5.QtCore import QThread, pyqtSignal
import re

class dgtransitionScrape_thread(QThread):
    finished = pyqtSignal(list)

    def __init__(self):
        super().__init__()

    def run(self):
        browser = mechanicalsoup.Browser()
        url = "https://www.dgtransitions.com/dental-practices-for-sale"
        page = browser.get(url)
        record_elements = page.soup.find_all('div', class_="sqs-html-content")
        record_elements = record_elements[2:9]
        dataArray = []

        # Use ThreadPoolExecutor to process li_elements concurrently
        for element in record_elements:
            p_tag = element.select_one("p")
            if p_tag and p_tag.strong:
                record = {
                    "website": "www.dgtransitions.com",
                    "origin": "https://www.dgtransitions.com/dental-practices-for-sale",
                    "state": "Washington",
                    "type": "General",
                    "city": "",
                    "operatory": 0,
                    "square_ft": "",
                    "price": "",
                    "annual_collections": "",
                    "valid": True,
                    "details": "",
                }
                record["source_link"] = record["origin"] + p_tag.strong.text
                record["name"] = p_tag.strong.text
                p_tag.strong.extract()
                admin_content = []

                pattern = r'(\d+)\s+Ops.*?Collecting\s+\$(\d+\.?\d*[MK]?\+?)'
                match = re.search(pattern, p_tag.text)
                if match:
                    record["operatory"] = int(match.group(1))  # First capturing group for Ops number
                    record["annual_collections"] = f"${match.group(2)}"
                    
                admin_content.append({ "key": "Contact for more details", "value": "Please email us at transitions@cpa4dds.com for prospectus. Link for NDA & HIPAA Form is at the top of this page, if you have not filled one out previously." })
                record["admin_content"] = admin_content
                dataArray.append(record)
        self.finished.emit(dataArray)