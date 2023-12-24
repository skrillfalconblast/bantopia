import requests

endpoint = "http://127.0.0.1:8000/"

get_response = requests.get(endpoint, data={'word' : 'hello'})

print(get_response.text)
