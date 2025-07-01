import mechanicalsoup
import concurrent
import requests
from concurrent.futures import ThreadPoolExecutor
from PyQt5.QtCore import QThread, pyqtSignal

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/114.0.0.0 Safari/537.36",
    "Referer": "https://westernpracticesales.com/",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest"
}


class westernPracticeSalesScrape_thread(QThread):
    finished = pyqtSignal(list)

    def __init__(self):
        super().__init__()

    def run(self):
        url = "https://westernpracticesales.com/wp-admin/admin-ajax.php?action=showAllListing"
        response = requests.get(url, headers=headers)
        json_data = response.json()
        dataArray = []

        # Use ThreadPoolExecutor to process li_elements concurrently
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(process_record_element, li) for li in json_data["allListings"]]

            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    dataArray.append(result)
                except Exception as e:
                    print(f"An error occurred: {e}")
        self.finished.emit(dataArray)


def process_record_element(record_element):
    with mechanicalsoup.StatefulBrowser() as browser:
        record = {
            "website": "westernpracticesales.com",
            "origin": "https://westernpracticesales.com/listings",
            "name": record_element.get("title", ""),
            "source_link": record_element.get("url", ""),
            "state": "",
            "city": "",
            "type": "",
            "operatory": 0,
            "square_ft": "",
            "price": "",
            "annual_collections": "",
            "valid": True
        }

        url = record["source_link"]
        if not url:
            print("Missing URL in record_element, skipping...")
            return record

        sub_page = browser.open(url, headers=headers)
        tr_tags = sub_page.soup.select("tr")[2:]

        for tr_tag in tr_tags:
            td_tags = tr_tag.select("td")
            if len(td_tags) == 2:
                key = td_tags[0].text.strip().replace(":", "")
                value_td = td_tags[1]

                if key == "Location":
                    span = value_td.select_one("span")
                    if span:
                        location_parts = span.text.strip().split(",")
                        if len(location_parts) == 2:
                            record["city"] = location_parts[0].strip()
                            record["state"] = location_parts[1].strip()
                        else:
                            record["city"] = span.text.strip()
                            record["state"] = ""
                            print(f"Unexpected location format: '{span.text.strip()}'")
                elif key == "Types of Practice":
                    record["type"] = value_td.text.strip()
                elif key == "Gross Collections":
                    span = value_td.select_one("span")
                    if span:
                        record["annual_collections"] = span.text.strip()

        asking_price_elem = sub_page.soup.select_one("div.listingBottomText > h3")
        if asking_price_elem and ":" in asking_price_elem.text:
            record["price"] = asking_price_elem.text.split(":", 1)[1].strip()
        else:
            record["price"] = ""
            print(f"Missing or malformed asking price on page: {url}")

        return record
