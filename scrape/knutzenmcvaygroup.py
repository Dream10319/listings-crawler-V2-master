import mechanicalsoup
from PyQt5.QtCore import QThread, pyqtSignal

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/114.0.0.0 Safari/537.36",
    "Referer": "https://knutzenmcvaygroup.com/",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest"
}

class knutzenmcvaygroupScrape_thread(QThread):
    finished = pyqtSignal(list)

    def __init__(self):
        super().__init__()

    def run(self):
        browser = mechanicalsoup.Browser()
        url = "https://knutzenmcvaygroup.com/washington"
        page = browser.get(url, headers=headers)
        record_elements = page.soup.find_all('div', class_="vc_column-inner")
        record_elements = record_elements[3:len(record_elements)]
        dataArray = []

        # Use ThreadPoolExecutor to process li_elements concurrently
        for element in record_elements:
            h2_tag = element.select_one('h2')
            if h2_tag:
                record = {
                    "origin": "https://knutzenmcvaygroup.com/washington",
                    "state": "Washington",
                    "type": "",
                    "city": "",
                    "operatory": 0,
                    "square_ft": "",
                    "price": "",
                    "annual_collections": "",
                    "valid": True
                }
                record["name"] = h2_tag.text
                record["source_link"] = record["origin"] + record["name"]
                p_tags = element.find_all("p")
                content = []
                admin_content = []

                accordion = element.find('div', class_="accordion_content_inner")
                last_a_tag = accordion.find_all('a')[-1]
                if "Download" in last_a_tag.text:
                    last_a_tag.extract()

                divs_to_remove = accordion.find_all('div', class_='vc_empty_space')
                for div_to_remove in divs_to_remove:
                    div_to_remove.extract()

                for p_tag in accordion.find_all('p'):
                     if ("for prospectus" in p_tag.text or "for more details" in p_tag.text) and "email" in p_tag.text.lower():
                        p_tag.extract()
                
                detail = str(accordion.find('div', class_='wpb_wrapper'))
                
                for index, p_tag in enumerate(p_tags):
                    # print(p_tag)
                    if p_tag.find('span', style='color: #ff0000;'):
                        content.append({ "key": 'Status', "value": p_tag.text })
                    elif index <= 1 and any('Description' in item for item in content) == False:
                        content.append({ "key": 'Description', "value": p_tag.text })
                        admin_content.append({ "key": 'Status', "value": p_tag.text })

                content.append({ 'Detail': detail })
                admin_content.append({ 'Detail': detail })

                record["content"] = content
                record["admin_content"] = admin_content
                dataArray.append(record)
        self.finished.emit(dataArray)