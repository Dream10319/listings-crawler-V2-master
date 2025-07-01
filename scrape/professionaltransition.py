import mechanicalsoup
import concurrent
from concurrent.futures import ThreadPoolExecutor
from PyQt5.QtCore import QThread, pyqtSignal

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/114.0.0.0 Safari/537.36",
    "Referer": "https://professionaltransition.com/",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest"
}

class professionalTransitionScrape_thread(QThread):
    finished = pyqtSignal(list)

    def __init__(self):
        super().__init__()

    def run(self):
        browser = mechanicalsoup.Browser()
        url = "https://professionaltransition.com/practices-for-sale"
        page = browser.get(url, headers=headers)
        record_elements = page.soup.find_all('div', class_="property_in_list")
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
            "website": "professionaltransition.com",
            "origin": "https://professionaltransition.com/practices-for-sale",
            "state": "",
            "type": "",
            "city": "",
            "operatory": 0,
            "square_ft": "",
            "price": "",
            "annual_collections": "",
            "valid": True,
            "details": ""
        }

        record["name"] = record_element.select("li")[1].text
        if "sold" in record["name"].lower():
            record["valid"] = False
        
        a_tag = record_element.select_one("a")
        if a_tag:
            href = a_tag["href"]
            sub_page = browser.get(href, headers=headers)   
            info = sub_page.soup.select_one("div.statMap_Container")
            record["state"] = info.select_one("li.property_city_att").select_one("span.value").text.strip()
            detail = sub_page.soup.select_one("div.wpp_the_content")
            # last_p_tag = detail.find_all('p')[-1]
            # last_p_tag.extract()
            # a_tags = detail.find_all("a")
            # for a_tag in a_tags:
            #     tag_text = a_tag.text
            #     a_tag.replace_with(tag_text)
            # admin_content.append({ "key":'Description', "value": str(detail) })
            record["source_link"] = href
            record["details"] = str(detail)
            return record