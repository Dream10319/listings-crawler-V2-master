import mechanicalsoup
import concurrent
from concurrent.futures import ThreadPoolExecutor
from PyQt5.QtCore import QThread, pyqtSignal
import json

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/114.0.0.0 Safari/537.36",
    "Referer": "https://mydentalbroker.com/",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest"
}

class mydentalbrokerScrape_thread(QThread):
    finished = pyqtSignal(list)

    def __init__(self):
        super().__init__()

    def run(self):
        records = []
        records.extend(get_hrefs("https://mydentalbroker.com/practices-for-sale/washington"))
        records.extend(get_hrefs("https://mydentalbroker.com/practices-for-sale/oregon"))
        records.extend(get_hrefs("https://mydentalbroker.com/practices-for-sale/idaho"))
        records.extend(get_hrefs("https://mydentalbroker.com/practices-for-sale/montana"))
        records.extend(get_hrefs("https://mydentalbroker.com/practices-for-sale/alaska"))
        records.extend(get_hrefs("https://mydentalbroker.com/practices-for-sale/hawaii"))
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

def get_hrefs(url):
    browser = mechanicalsoup.Browser()
    records = []
    try:
        page = browser.get(url, headers=headers)
        page_records = page.soup.find_all('div', class_="col_sale single-state")
        for record in page_records:
            a_tag = record.select_one("a")
            if a_tag:
                records.append(a_tag["href"])
        return records
    except Exception as e:
        print(f"An error occurred: {e}")

# Function to process each li_element
def process_record_element(href):
    with mechanicalsoup.StatefulBrowser() as browser:
        record = {
            "website": "mydentalbroker.com",
            "origin": "https://mydentalbroker.com/practices-for-sale",
            "source_link": href,
            "state": "",
            "type": "",
            "city": "",
            "operatory": 0,
            "square_ft": "",
            "price": "",
            "annual_collections": "",
            "valid": True,
            "details": "",
        }

        if "washington" in href:
            record["state"] = "Washington"
        elif "oregon" in href:
            record["state"] = "Oregon"
        elif "idaho" in href:
            record["state"] = "Idaho"         
        elif "montana" in href:
            record["state"] = "Montana"
        elif "alaska" in href:
            record["state"] = "Alaska"
        elif "hawaii" in href:
            record["state"] = 'Hawaii'

        sub_page = browser.get(href, headers=headers)   
        row = sub_page.soup.select("div.detail-col")[0]
        content_info = row.select_one("div.content-info")
        content_detail = row.select_one("div.content-detail")

        record["name"] = content_info.select_one("h1").text
        # record["city"] = content_info.select_one("p").text

        if "sold" in record["name"].lower() or "sale pending" in record["name"].lower():
            record["valid"] = False

        admin_content = []
        record["details"] = content_detail.select_one("p").text
        admin_content.append({ "key":"Detail", "value": content_detail.select_one("p").text })

        record["admin_content"] = admin_content
        return record