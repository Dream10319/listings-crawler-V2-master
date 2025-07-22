import mechanicalsoup
import concurrent
import json
from concurrent.futures import ThreadPoolExecutor
from PyQt5.QtCore import QThread, pyqtSignal

class mcvaytransitions_thread(QThread):
    finished = pyqtSignal(list)

    def __init__(self):
        super().__init__()

    def run(self):
        browser = mechanicalsoup.Browser()
        url = "https://www.mcvaytransitions.com/our-dental-practice-listings"
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
        "website": "www.mcvaytransitions.com",
        "origin": "https://www.mcvaytransitions.com/our-dental-practice-listings",
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
    # 1. SKIP if status is SOLD
    status_elem = li_element.select_one('div[id*="comp-m7pg9m0l1"] span.wixui-rich-text__text')
    if status_elem and status_elem.get_text(strip=True).upper() == "SOLD":
        return None  # Skip this record

    # 2. Name (city)
    name_elem = li_element.select_one('div[id*="comp-m7pg9m103"] h5')
    if name_elem:
        record["name"] = name_elem.get_text(strip=True)

    # 3. Price
    price_elem = li_element.select_one('div[id*="comp-m7pg9m0r"] span.wixui-rich-text__text')
    if price_elem:
        price_text = price_elem.get_text(strip=True)
        # If price is something like "$1,099,000", store it; otherwise, leave blank
        if price_text and "$" in price_text:
            record["price"] = price_text

    # 4. Source Link
    link_elem = li_element.select_one('a[data-testid="linkElement"]')
    if link_elem and link_elem.has_attr("href"):
        record["source_link"] = link_elem["href"]

    # Consider record invalid if name or link is missing
    if not record["name"] or not record["source_link"]:
        return None

    return record
