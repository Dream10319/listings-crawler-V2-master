import mechanicalsoup
import concurrent
from concurrent.futures import ThreadPoolExecutor
from PyQt5.QtCore import QThread, pyqtSignal
from lib.constants import practice_types
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/114.0.0.0 Safari/537.36",
    "Referer": "https://ctc-associates.com/",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest"
}

class ctcScrape_thread(QThread):
    finished = pyqtSignal(list)

    def __init__(self):
        super().__init__()

    def run(self):
        browser = mechanicalsoup.Browser()
        url = "https://ctc-associates.com/dental-practices-for-sale"
        page = browser.get(url)
        record_elements = page.soup.select("div.directory_listing")

        dataArray = []

        # Use ThreadPoolExecutor to process li_elements concurrently
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Submit tasks to the executor
            futures = [executor.submit(process_record_element, li) for li in record_elements]

            # Wait for all futures to complete
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    if result != None:
                        dataArray.append(result)  # If needed, you can use the result of each future here
                except Exception as e:
                    print(f"An error occurred: {e}")
        self.finished.emit(dataArray)

# Function to process each li_element
def process_record_element(record_element):
    with mechanicalsoup.StatefulBrowser() as browser:
        record = {
            "website": "ctc-associates.com",
            "origin": "https://ctc-associates.com/dental-practices-for-sale",
            "type": "",
            "state": "",
            "city": "",
            "operatory": 0,
            "square_ft": "",
            "price": "",
            "annual_collections": "",
            "valid": True,
            "details": ""
        }
        state_element = record_element.select("ul > li")[2]
        record["state"] = state_element.text.replace('STATE: ', '').strip()

        city_element = record_element.select("ul > li")[3]
        record["city"] = city_element.text.replace('AREA: ', '').strip()
        if record["city"] == 'TBD': record["city"] = ""

        a_tag = record_element.select_one("li.directory_link a")
        if a_tag:
            href = a_tag["href"]
            record["source_link"] = href

            sub_page = browser.open(href)

            ol = sub_page.soup.select_one("ol.breadcrumb")
            sheet_name = ol.select("li")[-1].text
            record["name"] = sheet_name
            # content = []
            admin_content = []

            # Add a new sheet
            detailDiv = sub_page.soup.select_one("ul.detailDiv")
            ul_elements = detailDiv.select("li > ul")

            for ul_element in ul_elements:
                li_items = ul_element.select("li")
                if len(li_items) >= 2:
                    key, value = li_items[0].text.strip(), li_items[1].text.strip()
                    # admin_content.append({ key: value })
                    lower_value = value.lower()
                    if key == 'Standing' and ("unavailable" in lower_value or "sold" in lower_value):
                        record["valid"] = False
                        
                    if key != 'Listing ID':
                        if key == 'Practice Type':
                            for type in practice_types:
                                lower_type = type.lower()
                                if lower_type in lower_value:
                                    record["type"] = type
                                    break
                        elif key == 'Number of Operatories':
                            if value != "":
                                record["operatory"] = int(re.findall(r'\d+', value)[0])
                        elif key == 'Approximate Square Feet':
                            record["square_ft"] = value
                        elif key == 'Purchase Price':
                            record["price"] = value
                        elif key == 'Gross Income':
                            record["annual_collections"] = value
                        # if key != "Additional Information":
                        #     content.append({ key: value })
                        if key == "Additional Information":
                            record["details"] = value
                            admin_content.append({ "key": key, "value": value })
                            
            # record["content"] = json.dumps(content)
            record["admin_content"] = admin_content
            return record