import mechanicalsoup
import concurrent
from concurrent.futures import ThreadPoolExecutor
from PyQt5.QtCore import QThread, pyqtSignal
from lib.constants import practice_types

class adsScrape_thread(QThread):
    finished = pyqtSignal(list)

    def __init__(self):
        super().__init__()

    def run(self):
        browser = mechanicalsoup.Browser()    
        baseUrl = "https://adsprecise.com/listings"
        basePage = browser.get(baseUrl)
        nav_element = basePage.soup.select(".fusion-tabs-1 > .nav")[0]

        tab_links = nav_element.select("a.tab-link")

        dataArray = []
        li_elements = []

        for tab_link in tab_links:
            page = browser.get(f"{baseUrl}{tab_link['href']}")

            li_elements.extend(page.soup.select(f"{tab_link['href']} .es-listing > .properties"))

            while True:
                pagination_lies = page.soup.select(f"{tab_link['href']} nav.pagination ul.page-numbers li")
                if len(pagination_lies) == 0:
                    break
                next_a_elements = pagination_lies[-1].select("a")
                if len(next_a_elements) == 0:
                    break

                url = next_a_elements[0]["href"]
                page = browser.get(url)
                li_elements.extend(page.soup.select(f"{tab_link['href']} .es-listing > .properties"))

        print(len(li_elements))
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(process_li_element, li) for li in li_elements]

            # Wait for all futures to complete
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    if result != None:
                        dataArray.append(result)  # If needed, you can use the result of each future here
                except Exception as e:
                    print(f"An error occurred: {e}")
        self.finished.emit(dataArray)

def process_li_element(li_element):
    with mechanicalsoup.StatefulBrowser() as browser:
        record = {
            "website": "adsprecise.com",
            "origin": "https://adsprecise.com/listings",
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
        a_tag = li_element.select(".es-read-wrap a")[0]
        if a_tag:
            href = a_tag["href"]
            record["source_link"] = href[:-1]            
            sub_page = browser.get(href)

            h1_element = sub_page.soup.select("h1.entry-title")[0]
            lower_value = h1_element.text.lower()
            if "sold" in lower_value:
                record["valid"] = False
            record["name"] = h1_element.text.strip()
            # content = []
            admin_content = []

            price_span = sub_page.soup.select_one("span.es-price")
            if price_span:
                record["price"] = price_span.text.strip()

            ul_element = sub_page.soup.select(".es-property-fields ul")[0]
            sub_li_elements = ul_element.select("li")

            for sub_li_element in sub_li_elements:
                key = sub_li_element.text.split(":")[0].strip()
                value = sub_li_element.text.split(":")[1].strip()
                if key == 'State':
                    record["state"] = value
                elif key == 'City':
                    record["city"] = value
                elif key == 'Practice Type':
                    lower_value = value.lower()
                    for type in practice_types:
                            lower_type = type.lower()
                            if lower_type in lower_value:
                                record["type"] = type
                                break
                elif key == 'Area':
                    record['square_ft'] = value
                # admin_content.append({ key: value })
                # if key not in ['Property ID','Listing #']:
                #     content.append({ key: value })

            description_elements = sub_page.soup.select("#es-description p")
            description = ""
            for description_element in description_elements:
                description += description_element.text
                lower_value = description_element.text.lower()
                if "sold" in lower_value:
                    record["valid"] = False
            if description != "":
                record["details"] = description
                admin_content.append({ "key": "description", "value": description })

            # record["content"] = json.dumps(content)
            record["admin_content"] = admin_content
            return record