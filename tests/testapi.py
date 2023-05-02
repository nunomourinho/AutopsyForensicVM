import requests

url = 'http://85.240.2.211:8000/api/test/'
api_key = 'd0397945-5c8b-432c-8cbf-010d4b8fc7fb'

headers = {
    'X-Api-Key': api_key
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    print('Access granted')
else:
    print('Access denied')
