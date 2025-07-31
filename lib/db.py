from PyQt5.QtCore import QThread, pyqtSignal
from pymongo import MongoClient
from lib.openai import chat_gpt
from lib.constants import build_prompt_ctcassociates, build_prompt_adsprecise, build_prompt_henryschein, build_prompt_menlotransitions, build_prompt_professionaltransition, build_prompt_ddsmatch, build_prompt_westernpractice
import os
import json

class save_data_thread(QThread):
    finished = pyqtSignal()

    def __init__(self, data_array):
        super().__init__()
        self.data_array = data_array

    def run(self):
        client = MongoClient(os.environ.get('MONGO_URL'),connectTimeoutMS=60000, socketTimeoutMS=60000)
        db = client[os.environ.get('MONGO_DATABASE')]
        collection = db[os.environ.get('MONGO_COLLECTION')]

        # Update or insert the new item into the table
        for data in self.data_array:
            try:
                exist_document = collection.find_one({"source_link": data['source_link']})
                if data["valid"] == False:
                    if exist_document:
                        collection.delete_one({"_id": exist_document["_id"]})
                else:
                    if data["website"] == "ctc-associates.com":
                        response_string = chat_gpt(prompt=build_prompt_ctcassociates(data["name"], data["details"], data["source_link"]))
                        response_string = response_string.replace("```", "").replace("json", "")
                        response = json.loads(response_string)
                        data["name"] = response["title"]
                        data["details"] = response["description"]
                        data["type"] = response["type"]
                        data["city"] = response["city"]
                        data["state"] = response["state"]
                        data["price"] = response["price"]
                    elif data["website"] == "adsprecise.com":
                        response_string = chat_gpt(prompt=build_prompt_adsprecise(data["name"], data["details"], data["source_link"]))
                        response_string = response_string.replace("```", "").replace("json", "")
                        response = json.loads(response_string)
                        data["name"] = response["title"]
                        data["details"] = response["description"]
                        data["operatory"] = response["operatory"]
                        data["annual_collections"] = response["annual_collections"]
                        data["type"] = response["type"]
                        data["city"] = response["city"]
                        data["state"] = response["state"]
                    elif data["website"] == "www.dentaltrans.com":
                        pass
                    elif data["website"] == "www.menlotransitions.com":
                        response_string = chat_gpt(prompt=build_prompt_adsprecise(data["name"], data["details"], data["source_link"]))
                        response_string = response_string.replace("```", "").replace("json", "")
                        response = json.loads(response_string)
                        data["name"] = response["title"]
                        data["details"] = response["description"]
                        data["operatory"] = response["operatory"]
                        data["annual_collections"] = response["annual_collections"]
                        data["type"] = response["type"]
                        data["city"] = response["city"]
                        data["state"] = response["state"]
                    elif data["website"] == "mydentalbroker.com":
                        response_string = chat_gpt(prompt=build_prompt_adsprecise(data["name"], data["details"], data["source_link"]))
                        response_string = response_string.replace("```", "").replace("json", "")
                        response = json.loads(response_string)
                        data["name"] = response["title"]
                        data["details"] = response["description"]
                        data["operatory"] = response["operatory"]
                        data["annual_collections"] = response["annual_collections"]
                        data["type"] = response["type"]
                        data["city"] = response["city"]
                        data["state"] = response["state"]
                    elif data["website"] == "professionaltransition.com":
                        response_string = chat_gpt(prompt=build_prompt_professionaltransition(data["details"], data["source_link"]))
                        response_string = response_string.replace("```", "").replace("json", "")
                        response = json.loads(response_string)
                        data["details"] = response["description"]
                        data["operatory"] = response["operatory"]
                        data["annual_collections"] = response["annual_collections"]
                        data["type"] = response["type"]
                        data["city"] = response["city"]
                        data["state"] = response["state"]
                    elif data["website"] == "ddsmatch.com":
                        response_string = chat_gpt(prompt=build_prompt_ddsmatch(data["name"], data["source_link"]))
                        response_string = response_string.replace("```", "").replace("json", "")
                        response = json.loads(response_string)
                        data["name"] = response["title"]
                        data["operatory"] = response["operatory"]
                        data["details"] = response["description"]
                        data["type"] = response["type"]
                        data["city"] = response["city"]
                        data["state"] = response["state"]
                    elif data["website"] == "omni-pg.com":
                        response_string = chat_gpt(prompt=build_prompt_professionaltransition(data["details"], data["source_link"]))
                        response_string = response_string.replace("```", "").replace("json", "")
                        response = json.loads(response_string)
                        data["details"] = response["description"]
                        data["operatory"] = response["operatory"]
                        data["annual_collections"] = response["annual_collections"]
                        data["type"] = response["type"]
                        data["city"] = response["city"]
                        data["state"] = response["state"]
                    elif data["website"] == "westernpracticesales.com":
                        response_string = chat_gpt(prompt=build_prompt_westernpractice(data["name"], data["source_link"]))
                        response_string = response_string.replace("```", "").replace("json", "")
                        response = json.loads(response_string)
                        data["name"] = response["title"]
                        data["details"] = response["description"]
                        data["operatory"] = response["operatory"]
                        data["annual_collections"] = response["annual_collections"]
                        data["type"] = response["type"]
                        data["city"] = response["city"]
                        data["state"] = response["state"]
                    elif data["website"] == "dentalpracticetransitions.henryschein.com":
                        response_string = chat_gpt(prompt=build_prompt_henryschein(data["name"], data["source_link"]))
                        response_string = response_string.replace("```", "").replace("json", "")
                        response = json.loads(response_string)
                        data["name"] = response["title"]
                        data["details"] = response["description"]
                        data["operatory"] = response["operatory"]
                        data["city"] = response["city"]
                        data["price"] = response["price"]
                    elif data["website"] == "www.dentalpractices4sale.com":
                        response_string = chat_gpt(prompt=build_prompt_westernpractice(data["name"], data["source_link"]))
                        response_string = response_string.replace("```", "").replace("json", "")
                        response = json.loads(response_string)
                        data["name"] = response["title"]
                        data["details"] = response["description"]
                        data["operatory"] = response["operatory"]
                        data["annual_collections"] = response["annual_collections"]
                        data["type"] = response["type"]
                        data["city"] = response["city"]
                        data["state"] = response["state"]
                        data["price"] = response["price"]
                    elif data["website"] == "www.mcvaytransitions.com":
                        response_string = chat_gpt(prompt=build_prompt_westernpractice(data["name"], data["source_link"]))
                        response_string = response_string.replace("```", "").replace("json", "")
                        response = json.loads(response_string)
                        data["name"] = response["title"]
                        data["details"] = response["description"]
                        data["operatory"] = response["operatory"]
                        data["annual_collections"] = response["annual_collections"]
                        data["type"] = response["type"]
                        data["city"] = response["city"]
                        data["state"] = response["state"]
                        data["price"] = response["price"]
                    elif data["website"] == "www.adstransitions.com":
                        response_string = chat_gpt(prompt=build_prompt_westernpractice(data["name"], data["source_link"]))
                        response_string = response_string.replace("```", "").replace("json", "")
                        response = json.loads(response_string)
                        data["name"] = response["title"]
                        data["details"] = response["description"]
                        data["operatory"] = response["operatory"]
                        data["annual_collections"] = response["annual_collections"]
                        data["type"] = response["type"]
                        data["city"] = response["city"]
                        data["state"] = response["state"]
                        data["price"] = response["price"]
                    if exist_document:
                        data.pop('valid', None)
                        collection.update_one({"_id": exist_document["_id"]}, {"$set": data})
                    else:
                        max_id_document = collection.find_one(sort=[('id', -1)])
                    
                        if max_id_document:
                            data['id'] = max_id_document['id'] + 1  # Set id to max_id + 1
                        else:
                            data['id'] = 1
                    
                        data.pop('valid', None)
                        collection.insert_one(data)
           
            except Exception as e:
                print(f"DB error occurred: {str(e)}")

        self.finished.emit()
