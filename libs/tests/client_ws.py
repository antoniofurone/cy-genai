import json
import requests
import pprint

# url="https://localhost:8000/llm-query"

# data = {"query" : "Quando è nato Salvatore Morelli ?","context_id":1}
# data_json = json.dumps(data)
# headers = {'Content-type': 'application/json','app-name':'test_app','app-key':'CyLang-9da11944-2fb0-462d-a79d-d586cf2f1625'}

# response = requests.post(url, data=data_json, headers=headers,verify=False)

# pprint.pprint(response.json())

url="https://localhost:8000/load-files/1"

data = {}
data_json = json.dumps(data)
headers = {'app-name':'test_app','app-key':'CyLang-9da11944-2fb0-462d-a79d-d586cf2f1625'}
files = {'file': open('C:/Users/User/VSProjects/cy-genai/libs/tests/italia.wav','rb')}
response = requests.post(url, headers=headers,data=data,files=files,verify=False)


pprint.pprint(response.json())

