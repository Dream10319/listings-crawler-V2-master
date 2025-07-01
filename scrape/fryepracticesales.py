import mechanicalsoup
import concurrent
import json
from concurrent.futures import ThreadPoolExecutor
from PyQt5.QtCore import QThread, pyqtSignal

class fryepracticesalesScrape_thread(QThread):
    finished = pyqtSignal(list)

    def __init__(self):
        super().__init__()

    def run(self):
        browser = mechanicalsoup.Browser()
        url = "https://www.fryepracticesales.com/properties"
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

# Function to process each li_element
def process_record_element(record_element):
    with mechanicalsoup.StatefulBrowser() as browser:
        record = {
            "origin": "https://www.fryepracticesales.com/properties",
            "state": "",
            "type": "",
            "city": "",
            "operatory": 0,
            "square_ft": "",
            "price": "",
            "annual_collections": ""
        }
        href = record_element.select_one("a")["href"]
        
        if href:
            record["state"] = "Arizona"
            record["city"] = ""
            elements = record_element.select("div > h2 > a")
            if "under contract" in elements[0].text.lower():
                record["sold"] = True
            record["name"] = elements[0].text
            record["signature"] = href

            content = []
            admin_content = []
            content.append({"Status": record_element.select_one("div > p > span > span").text })
            content.append({ "Annual collections": elements[1].text})
            admin_content.append({ "Title": record["name"] })
            admin_content.append({ "State": record["state"] })
            admin_content.append({"Status": record_element.select_one("div > p > span > span").text })
            admin_content.append({ "Annual collections": elements[1].text})
            sub_page = browser.open(record["signature"])

            spans = sub_page.soup.select("div > p > span")
            if "head back home" not in spans[0].text :
                admin_content.append({ "Property Description": spans[0].text})
                spans = spans[1:len(spans) - 1]
                key = "Contact Agent"
                contact = ""
                for index, pro in enumerate(spans):
                    stripped_text = pro.text.strip()
                    if stripped_text == 'Property Type' or stripped_text == 'Offices' or stripped_text == 'Asking Price' or stripped_text == 'Square Footage' or stripped_text == 'Year Built':
                        if stripped_text == 'Property Type':
                            admin_content.append({ key : contact })    
                        key = stripped_text
                    elif key == 'Contact Agent':
                        contact = contact + stripped_text
                        if spans[index + 1] != 'Property Type':
                            contact = contact + "<br/>"
                    else:
                        content.append({ key: stripped_text })
                        admin_content.append({ key: stripped_text })
                        
            record["content"] = json.dumps(content)
            record["admin_content"] = json.dumps(admin_content)
            return record