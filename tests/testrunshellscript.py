import requests


url = 'http://85.240.2.211:8000/api/run-script/'
api_key = 'd0397945-5c8b-432c-8cbf-010d4b8fc7fb'

headers = {
    'X-Api-Key': api_key
}

payload = {
    'script': 'whoamijj'
}

response = requests.post(url, headers=headers, json=payload)

if response.status_code == 200:
    print('Output:', response.json()['output'])
    print('Error code:', response.json()['error_code'])
else:
    print('Error:', response.json()['error'])
    print('Error code:', response.json()['error_code'])
