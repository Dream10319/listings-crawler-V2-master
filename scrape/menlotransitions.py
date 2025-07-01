import mechanicalsoup
from PyQt5.QtCore import QThread, pyqtSignal
import re

class menlotransactionScrape_thread(QThread):
    finished = pyqtSignal(list)

    def __init__(self):
        super().__init__()

    def run(self):
        browser = mechanicalsoup.Browser()
        page = browser.get("https://www.menlotransitions.com/region/arizona")
        arizona_records = page.soup.select("div.entry-content")
        page = browser.get("https://www.menlotransitions.com/region/california")
        california_records = page.soup.select("div.entry-content")
        page = browser.get("https://www.menlotransitions.com/region/florida")
        florida_records = page.soup.select("div.entry-content")
        dataArray = []

        for arizona in arizona_records:
            if "Just Sold!" in str(arizona):
                continue
            record = get_attributes(arizona, "Arizona")
            dataArray.append(record)
        for california in california_records:
            if "Just Sold!" in str(california):
                continue
            record = get_attributes(california, "California")
            dataArray.append(record)
        for florida in florida_records:
            if "Just Sold!" in str(florida):
                continue           
            record = get_attributes(florida, "Florida")
            dataArray.append(record)

        self.finished.emit(dataArray)

def get_attributes(element, state):
    record = {
        "website": "www.menlotransitions.com",
        "origin": "https://www.menlotransitions.com/current-listings",
        "state": state,
        "type": "",
        "city": "",
        "operatory": 0,
        "square_ft": "",
        "price": "",
        "annual_collections": "",
        "valid": True,
        "details": ""
    }
    name_atag = element.select_one("h4 > a")
    if name_atag.span:
        name_atag.span.extract()
    record["name"] = name_atag.text
    record["source_link"] = record["origin"] + "/" + record["name"]
    property_attributes = element.find('div', class_='property-attributes')

    # Extract the text content
    text_content = property_attributes.get_text(separator='|', strip=True)

    # Split the text by "<br>"
    splits_by_br = text_content.split('|')
    content = []
    # admin_content = []

    for index, split in enumerate(splits_by_br):
        if ":" in split:
            if index + 1 < len(splits_by_br) and ":" not in splits_by_br[index + 1]:
                # content.append({ split.strip()[:-1] : splits_by_br[index + 1].strip() })
                # admin_content.append({ split.strip()[:-1] : splits_by_br[index + 1].strip() })
                if split.strip()[:-1] == 'Annual Collections':
                    record["annual_collections"] = splits_by_br[index + 1].strip()
                elif split.strip()[:-1] == 'Price':
                    if splits_by_br[index + 1].strip() != "TBD":
                        record["price"] = splits_by_br[index + 1].strip()
                elif split.strip()[:-1] == 'Operatories':
                    record["operatory"] = int(re.findall(r'\d+', splits_by_br[index + 1].strip())[0])
            # else:
                # content.append({ split.strip()[:-1]: "" })
                # admin_content.append({ split.strip()[:-1]: "" })
                
    p_tags = element.find('div', class_="property-attributes archive highlights").select("p")
    highlights = ""
    for index, p in enumerate(p_tags):
        highlights = highlights + p.text
        if index < len(p_tags) - 1:
            highlights = highlights + "\n"
    record["details"] = highlights
    content.append({ "key": "Pratice Hightlights", "value": highlights })
    
    record["content"] = content
    # record["admin_content"] = json.dumps(admin_content)
    return record