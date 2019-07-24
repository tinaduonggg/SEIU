import requests

r = requests.get('https://data.medicare.gov/resource/eqxu-aw4f.json')
result = r.json()
print(result)
