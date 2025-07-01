from bs4 import BeautifulSoup
import requests
from PyQt5.QtCore import QThread, pyqtSignal

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/114.0.0.0 Safari/537.36",
    "Referer": "https://ddsmatch.com/",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest"
}

class ddsmatchScrape_thread(QThread):
    finished = pyqtSignal(list)

    def __init__(self):
        super().__init__()

    def run(self):
        records = []
        page = 1
        while True:
            url= "https://ddsmatch.com/?sfid=240283&sf_action=get_data&sf_data=all&_sfm_revenue=0+100000000&_sfm_operatories=0+1000&sf_paged={}&lang=en".format(page)
            response = requests.get(url, headers=headers)
            json_data = response.json()
            soup = BeautifulSoup(json_data["results"], 'html.parser')
            record_elements = soup.find_all('div', class_="search-filter-result-item")
            if len(record_elements) != 0:
                records.extend(record_elements)
                page = page + 1
            else: break

        dataArray = []
        for li in records:
            try:
                result = process_record_element(li)
                dataArray.append(result)  # If needed, you can use the result of each future here
            except Exception as e:
                print(f"An error occurred: {e}")
        self.finished.emit(dataArray)

# Function to process each li_element
def process_record_element(record_element):
    record = {
        "website": "ddsmatch.com",
        "origin": "https://ddsmatch.com/dental-practice-listings",
        "state": "",
        "type": "",
        "city": "",
        "operatory": 0,
        "square_ft": "",
        "price": "",
        "annual_collections": "",
        "valid": True
    }
    h3_tags = record_element.select("h3.title")
    if len(h3_tags) > 1:
        name_tag = h3_tags[0].find('p')
        link_tag = h3_tags[1].find('a')

        record["name"] = name_tag.get_text(strip=True) if name_tag else ""
        record["source_link"] = link_tag.get("href", "") if link_tag else ""
        if not record["source_link"]:
            raise ValueError("Missing source link")
    # content = []
    # admin_content = []
    
    location = record_element.select_one("div.experience")
    if location:
        location_key_value = location.text.split(":")
        if location_key_value[1]:
            if len(location_key_value[1].split(",")) > 1:
                record["state"] = location_key_value[1].split(",")[1].strip()
                record["city"] = location_key_value[1].split(",")[0].strip()
            else:
                record["state"] = ""
                record["city"] = location_key_value[1].strip()
        
    revenue_key_value = record_element.select_one("div.revenue")
    if revenue_key_value:
        revenue_key_value = revenue_key_value.text.split(":")
        if revenue_key_value[1]:
            record["annual_collections"] = revenue_key_value[1].strip()
    
    education_key_value = record_element.select_one("div.education")
    if education_key_value:
        education_key_value = education_key_value.text.split(":")
        record["operatory"] = int(education_key_value[1].strip())
        # content.append({education_key_value[0].strip(): education_key_value[1].strip() })
        # admin_content.append({education_key_value[0].strip(): education_key_value[1].strip() })
    
    # grad_year_key_value = record_element.select_one("div.grad_year")
    # if grad_year_key_value:
    #     grad_year_key_value = grad_year_key_value.text.split(":")
    #     content.append({grad_year_key_value[0].strip(): grad_year_key_value[1].strip() })
    #     admin_content.append({grad_year_key_value[0].strip(): grad_year_key_value[1].strip() })
    
    specialty_key_value = record_element.select_one("div.specialty")
    if specialty_key_value:
        specialty_key_value = specialty_key_value.text.split(":")
        if specialty_key_value[1]:
            record["type"] = specialty_key_value[1].strip()
        # content.append({"Type of Practice": specialty_key_value[1].strip() })
        # admin_content.append({"Type of Practice": specialty_key_value[1].strip() })
        
    # opportunity = record_element.select_one("div.opportunity > ul")
    # if opportunity:
        # content.append({"Opportunity": str(opportunity) })
        # admin_content.append({"Opportunity": str(opportunity) })
        # record["operatory"] = opportunity
    # else:
        # opportunity_key_value = record_element.select_one("div.opportunity").text.split(":")
        # content.append({"Opportunity": opportunity_key_value[1].strip() })
        # admin_content.append({"Opportunity": opportunity_key_value[1].strip() })
        # if opportunity_key_value[1]:
        #     record["operatory"] = opportunity_key_value[1].strip()
    
    # favoritee_key_value = record_element.select_one("div.favoritee > p")
    # if favoritee_key_value:
    #     favoritee_key_value = favoritee_key_value.text.split(":")
    #     admin_content.append({favoritee_key_value[0].strip(): favoritee_key_value[1].strip() })

    # record["content"] = json.dumps(content)
    # record["admin_content"] = json.dumps(admin_content)
    return record