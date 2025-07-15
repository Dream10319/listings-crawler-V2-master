import mechanicalsoup
import concurrent
import json
from concurrent.futures import ThreadPoolExecutor
from PyQt5.QtCore import QThread, pyqtSignal

class dental4sale_thread(QThread):
    finished = pyqtSignal(list)

    def __init__(self):
        super().__init__()

    def run(self):
        browser = mechanicalsoup.Browser()
        url = "https://www.dentalpractices4sale.com/dental-offices"
        page = browser.get(url)
        record_elements = page.soup.select_one('[role="list"]').select('[role="listitem"]')

        dataArray = []

        # # Use ThreadPoolExecutor to process li_elements concurrently
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Submit tasks to the executor
            futures = [executor.submit(process_record_element, li) for li in record_elements]

            # Wait for all futures to complete
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    dataArray.append(result)  # If needed, you can use the result of each future here
                except Exception as e:
                    print(f"An error occurred: {e}")
        self.finished.emit(dataArray)

def process_record_element(li_element):
    record = {
        "website": "www.dentalpractices4sale.com",
        "origin": "https://www.dentalpractices4sale.com/dental-offices",
        "type": "",
        "state": "",
        "city": "",
        "operatory": 0,
        "square_ft": "",
        "price": "",
        "annual_collections": "",
        "valid": True,
        "details": "",
        "name": "",
        "source_link": "",
    }
    # Name/title
    h2 = li_element.select_one('div[id*="comp-lmpr3cwc"] h2')
    if h2:
        record["name"] = h2.get_text(strip=True)
    # Details/Overview
    overview = li_element.select_one('div[id*="comp-lmpr5w20"] p')
    if overview:
        record["details"] = overview.get_text(strip=True)
    # Type (often "Type" field below)
    type_label = li_element.find('div', id=lambda x: x and 'comp-lmpsj1vq' in x)
    if type_label and type_label.find_next_sibling():
        type_value = type_label.find_next_sibling().get_text(strip=True)
        record["type"] = type_value
    # Square feet/size
    size_label = li_element.find('div', id=lambda x: x and 'comp-lmpsixcl' in x)
    if size_label and size_label.find_next_sibling():
        size_value = size_label.find_next_sibling().get_text(strip=True)
        record["square_ft"] = size_value
    # Status (skip if UNDER CONTRACT)
    status_label = li_element.find('div', id=lambda x: x and 'comp-lmpshb77' in x)
    if status_label and status_label.find_next_sibling():
        status_value = status_label.find_next_sibling().get_text(strip=True).upper()
        if "UNDER CONTRACT" in status_value:
            return None  # SKIP this record
    # Link
    a_tag = li_element.select_one('a[data-testid="linkElement"]')
    if a_tag:
        record["source_link"] = a_tag['href']
    return record