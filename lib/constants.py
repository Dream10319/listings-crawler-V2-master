from bs4 import BeautifulSoup
import requests


practice_types = ['Pedo', 'Perio', 'Ortho', 'Endo', 'General', 'Surgery']

def build_prompt_ctcassociates(title, description, link):
    full_content = extract_full_text_from_link(link)
    prompt = f"""
        Your task is to rewrite the title and description from full content and original title and description.
        And need to get city and state, practice, price type also.

        Title: "{title}"
        Description: "{description}"
        Full content: "{full_content}"
        
        **Requirements**
        - Exclude email addresses, URLs, and phone numbers, first and last names
        - Exclude listing #’s or listing IDs or CODES numbers or Serial Numbers. 
        
        **Output JSON Format**
        The output must adhere to the following structure:
        {{
            "title": "",
            "description": "",
            "city": "",
            "state": "",
            "type": "",
            "price":""
        }}

        **Output**
        Please provide the result strictly in JSON format, without any additional commentary or explanations.
    """ 
    return prompt

def build_prompt_menlotransitions(title, description):
    prompt = f"""
        Your task is to rewrite the title and description from full content and original title and description.

        Title: "{title}"
        Description: "{description}"
        
        **Requirements**
        - Exclude email addresses, URLs, and phone numbers, first and last names
        - Exclude listing #’s or listing IDs or CODES numbers or Serial Numbers. 
        
        **Output JSON Format**
        The output must adhere to the following structure:
        {{
            "title": "",
            "description": "",
        }}

        **Output**
        Please provide the result strictly in JSON format, without any additional commentary or explanations.
    """ 
    return prompt

def build_prompt_adsprecise(title, description, link):
    full_content = extract_full_text_from_link(link)
    prompt = f"""
        Your task is to rewrite the title and description and extract collections and number of operatories from full content and original title and description.
        And need to get city and state, practice type also.

        Title: "{title}"
        Description: "{description}"
        Full content: "{full_content}"

        **Requirements**
        - Exclude email addresses, URLs, and phone numbers, first and last names
        - Exclude listing #’s or listing IDs or CODES numbers or Serial Numbers.
        
        **Output JSON Format**
        The output must adhere to the following structure:
        {{
            "title": "",
            "description": "",
            "operatory": Number,
            "annual_collections: "",
            "city": "",
            "state": "",
            "type": ""
        }}

        **Output**
        Please provide the result strictly in JSON format, without any additional commentary or explanations.
    """ 
    return prompt

def build_prompt_professionaltransition(description, link):
    full_content = extract_full_text_from_link(link)
    prompt = f"""
        Your task is to rewrite description within 2 sentences and extract collections and number of operatories from full content and original description.
        And need to get city and state, practice type also.

        Description: "{description}"
        Full content: "{full_content}"

        **Requirements**
        - Exclude email addresses, URLs, and phone numbers, first and last names
        - Exclude listing #’s or listing IDs or CODES numbers or Serial Numbers.
        
        **Output JSON Format**
        The output must adhere to the following structure:
        {{
            "title": "",
            "description": "",
            "operatory": Number,
            "annual_collections: "",
            "city": "",
            "state": "",
            "type": ""
        }}

        **Output**
        Please provide the result strictly in JSON format, without any additional commentary or explanations.
    """ 
    return prompt

def build_prompt_ddsmatch(title, link):
    full_content = extract_full_text_from_link(link)
    prompt = f"""
        Your task is to rewrite the title and description from full content and original title.
        And need to get city and state, operatory,  practice type also.

        Title: "{title}"
        Full content: "{full_content}"
        
        **Requirements**
        - Exclude email addresses, URLs, and phone numbers, first and last names
        - Exclude listing #’s or listing IDs or CODES numbers or Serial Numbers. 
        
        **Output JSON Format**
        The output must adhere to the following structure:
        {{
            "title": "",
            "description": "",
            "operatory": Number,
            "city": "",
            "state": "",
            "type": ""
        }}

        **Output**
        Please provide the result strictly in JSON format, without any additional commentary or explanations.
    """ 
    return prompt

def build_prompt_westernpractice(title, link):
    full_content = extract_full_text_from_link(link)
    prompt = f"""
        Your task is to rewrite the title and description from full content and original title.
        And need to get city and state, practice type also.

        Title: "{title}"
        Full content: "{full_content}"
        
        **Requirements**
        - Exclude email addresses, URLs, and phone numbers, first and last names
        - Exclude listing #’s or listing IDs or CODES numbers or Serial Numbers. 
        
        **Output JSON Format**
        The output must adhere to the following structure:
        {{
            "title": "",
            "description": "",
            "operatory": Number,
            "annual_collections: "",
            "city": "",
            "state": "",
            "type": "",
            "price":""
        }}

        **Output**
        Please provide the result strictly in JSON format, without any additional commentary or explanations.
    """ 
    return prompt

def build_prompt_henryschein(title, link):
    full_content = extract_full_text_from_link(link)
    prompt = f"""
        Your task is to rewrite the title and description from full content and original title.
        And need to get city, price and operatory.

        Title: "{title}"
        Full content: "{full_content}"
        
        **Requirements**
        - Exclude email addresses, URLs, and phone numbers, first and last names
        - Exclude listing #’s or listing IDs or CODES numbers or Serial Numbers. 
        
        **Output JSON Format**
        The output must adhere to the following structure:
        {{
            "title": "",
            "description": "",
            "operatory": Number,
            "city": "",
            "price": "",
        }}

        **Output**
        Please provide the result strictly in JSON format, without any additional commentary or explanations.
    """ 
    return prompt

def extract_full_text_from_link(link):
    try:
        response = requests.get(link, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"})
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove unwanted elements like scripts and styles
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        full_text = soup.get_text(separator=" ", strip=True)
        return full_text

    except Exception as e:
        print(f"[ERROR] Failed to fetch or parse link: {e}")
        return ""