import mechanicalsoup
import concurrent
from concurrent.futures import ThreadPoolExecutor
from PyQt5.QtCore import QThread, pyqtSignal

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/114.0.0.0 Safari/537.36",
    "Referer": "https://dentalpracticetransitions.henryschein.com/",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest"
}

class henryscheinScrape_thread(QThread):
    finished = pyqtSignal(list)

    def __init__(self):
        super().__init__()

    def run(self):
        records = []
        browser = mechanicalsoup.Browser()

        index = 0
        while True:
            if index == 1:
                index = 2
            url = "https://dentalpracticetransitions.henryschein.com/listings/page/" + str(index) + "/"
            page = browser.get(url, headers=headers)
            record_elements = page.soup.select("div.archive-single-salesforce-listing")
            if len(record_elements) != 0:
                records.extend(record_elements)
            else: 
                break
            index = index + 1

        dataArray = []

        # Use ThreadPoolExecutor to process li_elements concurrently
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Submit tasks to the executor
            futures = [executor.submit(process_record_element, li) for li in records]

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
    record = {
        "website": "dentalpracticetransitions.henryschein.com",
        "origin": "https://dentalpracticetransitions.henryschein.com/listings",
        "state": "",
        "type": "",
        "city": "",
        "operatory": 0,
        "square_ft": "",
        "price": "",
        "annual_collections": "",
        "details": "",
        "valid": True
    }

    # Extract status
    status_div = record_element.select_one("div.tags-single")
    if status_div and "sold" in status_div.text.strip().lower():
        record["valid"] = False

    # Extract name/city
    name_tag = record_element.select_one("h3")
    if name_tag:
        record["name"] = name_tag.text.strip()
        record["city"] = name_tag.text.strip()

    # Extract rundown info (State, Practice Type, Gross Collections, Listing Code)
    rundown_tags = record_element.select("p.md-listing-rundown-data")
    for tag in rundown_tags:
        label = tag.select_one("span.data-label")
        value = tag.select("span")[1] if len(tag.select("span")) > 1 else None

        if label and value:
            key = label.text.strip().rstrip(":")
            val = value.text.strip()

            if key == "State":
                record["state"] = val
            elif key == "Practice Type":
                record["type"] = val
            elif key == "Gross Collections":
                record["annual_collections"] = val
            elif key == "Listing Code":
                record["source_link"] = f"https://dentalpracticetransitions.henryschein.com/listings/{val}"

    # Extract description
    desc = record_element.select_one("p.description")
    if desc:
        record["details"] = desc.text.strip()

    return record