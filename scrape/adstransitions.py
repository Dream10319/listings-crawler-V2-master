import mechanicalsoup
import concurrent
import json
from concurrent.futures import ThreadPoolExecutor
from PyQt5.QtCore import QThread, pyqtSignal

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/114.0.0.0 Safari/537.36",
    "Referer": "https://www.adstransitions.com/",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest"
}

class adstransitionScrape_thread(QThread):
    finished = pyqtSignal(list)

    def __init__(self):
        super().__init__()

    def run(self):
        browser = mechanicalsoup.Browser()
        url = "https://www.adstransitions.com/practices-for-sale"
        page = browser.get(url, headers=headers)
        href_elements = page.soup.select(".view-all")
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

# Function to process each li_element
def process_href_element(href_element):
    with mechanicalsoup.StatefulBrowser() as browser:
        record = {
            "origin": "https://www.adstransitions.com/practices-for-sale",
            "state": "",
            "type": "",
            "city": "",
            "operatory": 0,
            "square_ft": "",
            "price": "",
            "annual_collections": ""
        }
        href = href_element["href"]
        record["signature"] = href[:-1]
        sub_page = browser.get(href, headers=headers)

        h1_element = sub_page.soup.select(".profile-page > .row h1")[0]
        record["name"] = h1_element.text

        divs = sub_page.soup.select(".profile-page > div.col-md-8 > div.col-md-6")
        pairs = []
        content = []
        admin_content = []
        admin_content.append({ 'Title': record["name"] })

        for i in range(0, len(divs), 2):
            odd = divs[i].text.strip()
            even = divs[i+1].text.strip()
            pairs.append((odd, even))
        
        for odd, even in pairs:
            if odd == 'State':
                record["state"] = even
                admin_content.append({ 'State': even })
            elif odd == 'City or Advertised Area':
                record["city"] = even
                admin_content.append({ 'City': even })
            else:
                admin_content.append({ odd: even })
            if odd != 'Listing Reference Number':
                content.append({ odd: even })

        admin_content.append({"phone":sub_page.soup.select(".info-card-detail")[0].text.strip()})
        admin_content.append({"email": sub_page.soup.select(".info-card-detail")[1].text.strip()})

        record["content"] = json.dumps(content)
        record["admin_content"] = json.dumps(admin_content)
        return record