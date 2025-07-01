import mechanicalsoup
import concurrent
import json
from concurrent.futures import ThreadPoolExecutor
from PyQt5.QtCore import QThread, pyqtSignal

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/114.0.0.0 Safari/537.36",
    "Referer": "https://omni-pg.com/",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest"
}

class omniScrape_thread(QThread):
    finished = pyqtSignal(list)

    def __init__(self):
        super().__init__()

    def run(self):
        browser = mechanicalsoup.Browser()
        url = "https://omni-pg.com/practices-for-sale"
        page = browser.get(url, headers=headers)
        record_elements = page.soup.select("div.col-sm-4")
        dataArray = []

         # Use ThreadPoolExecutor to process li_elements concurrently
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

# Function to process each li_element
def process_record_element(record_element):
    with mechanicalsoup.StatefulBrowser() as browser:
        record = {
            "website": "omni-pg.com",
            "origin": "https://omni-pg.com/practices-for-sale",
            "state": "",
            "type": "",
            "city": "",
            "operatory": 0,
            "square_ft": "",
            "price": "",
            "annual_collections": "",
            "valid": True,
        }

        a_tags = record_element.select("a")
        for a_tag in a_tags:
            if a_tag.text == 'LEARN MORE':
                record["source_link"] = a_tag["href"]
                break

        if record["source_link"]:
            sub_page = browser.get(record["source_link"], headers=headers) 
            record["name"] = sub_page.soup.select_one("h3.adv-headline-h3").text.strip()
            div_tags = sub_page.soup.select("div.wpb_text_column")
            record["city"] = div_tags[6].text.strip()
            record["details"] = div_tags[5].text.strip()
            return record