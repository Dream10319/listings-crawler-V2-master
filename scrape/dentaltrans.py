import mechanicalsoup
import concurrent
from concurrent.futures import ThreadPoolExecutor
from PyQt5.QtCore import QThread, pyqtSignal
from lib.constants import practice_types

class dentaltranScrape_thread(QThread):
    finished = pyqtSignal(list)

    def __init__(self):
        super().__init__()

    def run(self):
        browser = mechanicalsoup.Browser()
        url = "https://www.dentaltrans.com/listings"
        page = browser.get(url)
        record_elements = page.soup.select("a.summary-thumbnail-container")

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
            "website": "www.dentaltrans.com",
            "origin": "https://www.dentaltrans.com/listings",
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
        href = record_element["href"]
        if href:
            record["state"] = "Colorado"
            record["source_link"] = "https://www.dentaltrans.com" + href
            sub_page = browser.open(record["source_link"])
            item_title = sub_page.soup.select_one("h1.BlogItem-title").text
            if "sold" in item_title.lower() or "under contract" in item_title.lower():
                record["valid"] = False
            record["name"] = item_title

            elements = sub_page.soup.select('[data-block-type="2"]')
            p_tags = elements[0].select("p") 
            # content = []
            # admin_content = []
            
            for p_tag in p_tags:
                parts = p_tag.text.split(":")
                key = parts[0].strip()
                value = ""
                if len(parts) == 2:
                    value = parts[1].strip()
                if key == 'Location':
                    record["city"] = value
                elif key == 'Practice Type':
                    lower_value = value.lower()
                    for type in practice_types:
                        lower_type = type.lower()
                        if lower_type in lower_value:
                            record["type"] = type
                            break
                elif key == 'Number of Operatories' and value != "":
                    if value.isdigit():
                        record["operatory"] = int(value)
                elif key == "Gross Income":
                    record["annual_collections"] = value
                
            # record["content"] = json.dumps(content)
            # record["admin_content"] = json.dumps(admin_content)
            p_tags = elements[1].select("p")
            if p_tags[0].text and "Non-Disclosure form" not in p_tags[0].text:
                record["details"] = p_tags[0].text
            return record