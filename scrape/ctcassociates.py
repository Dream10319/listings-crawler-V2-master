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
    # Skip if listing is sold or pending
    class_list = record_element.get("class", [])
    if "sold" in class_list or "pending" in class_list:
        return None

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
        "details": "",
        "source_link": "",
        "name": "",
        "admin_content": []
    }

    li_elements = record_element.select("ul > li")

    # Set source link and name
    a_tag = record_element.select_one("li.directory_link a")
    if a_tag:
        record["source_link"] = "https://ctc-associates.com" + a_tag["href"]
        record["name"] = a_tag.text.strip()

    # Extract key details from available inline fields
    for li in li_elements:
        text = li.get_text(strip=True)
        if "TYPE:" in text:
            record["type"] = li.text.replace("TYPE:", "").strip()
        elif "STATE:" in text:
            record["state"] = li.text.replace("STATE:", "").strip()
        elif "AREA:" in text:
            city = li.text.replace("AREA:", "").strip()
            record["city"] = "" if city == "TBD" else city
        elif "COLLs:" in text:
            record["annual_collections"] = li.text.replace("COLLs:", "").strip()
        elif "OPs:" in text:
            match = re.search(r'\d+', li.text)
            if match:
                record["operatory"] = int(match.group())
        elif "REF#:" in text:
            value = li.text.replace("REF#:", "").strip()
            if value.lower() in ["sold", "under contract", "unavailable"]:
                record["valid"] = False
        elif "NET:" in text:
            # optionally include in admin content
            record["admin_content"].append({
                "key": "Net Income",
                "value": li.text.replace("NET:", "").strip()
            })

    return record