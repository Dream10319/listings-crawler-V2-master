from bs4 import BeautifulSoup
import requests
from PyQt5.QtCore import QThread, pyqtSignal
import concurrent
from concurrent.futures import ThreadPoolExecutor

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
            url = "https://ddsmatch.com/?sfid=240283&sf_action=get_data&sf_data=all&_sfm_revenue=0+100000000&_sfm_operatories=0+1000&sf_paged={}&lang=en".format(page)
            response = requests.get(url, headers=headers)
            json_data = response.json()
            soup = BeautifulSoup(json_data["results"], 'html.parser')

            # Grab all potential record elements
            raw_elements = soup.find_all('div', class_="search-filter-result-item")

            # Filter out elements that contain the word "MATCHED!" (case-sensitive, as per source)
            record_elements = []
            for el in raw_elements:
                matched_tag = el.find('div', class_='launch')
                if matched_tag and "MATCHED!" in matched_tag.get_text(strip=True):
                    continue  # skip MATCHED listings
                record_elements.append(el)

            # Break if no non-MATCHED records remain
            if record_elements:
                records.extend(record_elements)
                page += 1
            else:
                break
            
        dataArray = []

        # Use ThreadPoolExecutor to process li_elements concurrently
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Submit tasks to the executor
            futures = [executor.submit(process_record_element, li) for li in records]

            # Wait for all futures to complete
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    if result != None:
                        dataArray.append(result)  # If needed, you can use the result of each future here
                except Exception as e:
                    print(f"An error occurred: {e}")
        self.finished.emit(dataArray)


# Function to process each li_element
def process_record_element(record_element):
    # Skip if "MATCHED!" is present
    match_tag = record_element.select_one("h3.view_profile2 p")
    if match_tag and "MATCHED!" in match_tag.get_text(strip=True).upper():
        return None

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
        "valid": True,
        "name": "",
        "source_link": ""
    }

    # Get all h3.title tags
    h3_tags = record_element.select("h3.title")

    if len(h3_tags) >= 1:
        name_tag = h3_tags[0].find("p")
        if name_tag:
            record["name"] = name_tag.get_text(strip=True)

    if len(h3_tags) >= 2:
        link_tag = h3_tags[1].find("a")
        if link_tag:
            record["source_link"] = link_tag.get("href", "").strip()
            record["name"] = record["name"] or link_tag.get_text(strip=True)
        else:
            # Fallback if no <a>, get plain text ID
            p_tag = h3_tags[1].find("p")
            if p_tag:
                record["name"] = record["name"] or p_tag.get_text(strip=True)

    if not record["source_link"]:
        # Try fallback: any <a> in "view_profile"
        view_link = record_element.select_one("h3.view_profile a")
        if view_link:
            record["source_link"] = view_link.get("href", "").strip()

    if not record["source_link"]:
        raise ValueError("Missing source link")

    # Location
    location_tag = record_element.select_one("div.experience")
    if location_tag:
        location_text = location_tag.get_text(strip=True).replace("Location:", "").strip()
        if "," in location_text:
            city, state = location_text.split(",", 1)
            record["city"] = city.strip()
            record["state"] = state.strip()
        else:
            record["city"] = location_text

    # Revenue / Annual Collections
    revenue_tag = record_element.select_one("div.revenue")
    if revenue_tag:
        revenue_text = revenue_tag.get_text(strip=True).replace("Revenue:", "").strip()
        if revenue_text.upper() != "N/A":
            record["annual_collections"] = revenue_text

    # Operatories
    education_tag = record_element.select_one("div.education")
    if education_tag:
        education_text = education_tag.get_text(strip=True).replace("Operatories:", "").strip()
        try:
            record["operatory"] = int(education_text)
        except ValueError:
            pass  # ignore if not an integer

    # Practice Type
    specialty_tag = record_element.select_one("div.specialty")
    if specialty_tag:
        type_text = specialty_tag.get_text(strip=True).replace("Type:", "").strip()
        record["type"] = type_text

    return record

