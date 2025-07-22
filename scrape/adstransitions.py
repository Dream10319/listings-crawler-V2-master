import mechanicalsoup
import concurrent
import json
from concurrent.futures import ThreadPoolExecutor
from PyQt5.QtCore import QThread, pyqtSignal

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
}

class adstransitionScrape_thread(QThread):
    finished = pyqtSignal(list)

    def __init__(self):
        super().__init__()

    def run(self):
        browser = mechanicalsoup.Browser()
        url = "https://www.adstransitions.com/practices-for-sale/"
        page = browser.get(url, headers=headers)
        href_elements = page.soup.select(".prac-for-sale-block")

        dataArray = []

        # Use ThreadPoolExecutor to process li_elements concurrently
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Submit tasks to the executor
            futures = [executor.submit(process_href_element, li) for li in href_elements]

            # Wait for all futures to complete
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    dataArray.append(result)  # If needed, you can use the result of each future here
                except Exception as e:
                    print(f"An error occurred: {e}")
        self.finished.emit(dataArray)

def process_href_element(href_element):
    # href_element is a BeautifulSoup element representing .prac-for-sale-block

    record = {
        "website": "www.adstransitions.com",
        "origin": "https://www.adstransitions.com/practices-for-sale",
        "type": "",
        "state": "",
        "city": "",
        "operatory": "",
        "square_ft": "",
        "price": "",
        "annual_collections": "",
        "valid": True,
        "details": "",
        "name": "",
        "source_link": "",
    }
    # Get name (title)
    try:
        record["name"] = href_element.select_one("h3.list-heading").get_text(strip=True)
    except Exception:
        record["name"] = ""

    # Get source link
    try:
        record["source_link"] = href_element.select_one("a.view-list-button")["href"]
    except Exception:
        record["source_link"] = ""

    # Parse the details table
    content = []
    admin_content = []
    details_table = href_element.select_one("table.list-table")
    skip_listing = False
    if details_table:
        for row in details_table.select("tr"):
            label_td = row.select_one("td.list-label")
            value_td = row.select_one("td.label-value span")
            if not label_td or not value_td:
                continue
            label = label_td.get_text(strip=True).replace(":", "")
            value = value_td.get_text(strip=True)
            content.append({label: value})
            admin_content.append({label: value})
            if label == "State":
                record["state"] = value
            elif label in ["City", "City or Advertised Area"]:
                record["city"] = value
            elif label == "Status Type" and value.lower() == "under contract":
                skip_listing = True
            elif label == "Operatories":
                record["operatory"] = value

    if skip_listing:
        return None  # Skip this listing
    return record