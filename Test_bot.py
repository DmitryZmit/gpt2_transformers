import requests

url = "https://api.telegram.org/bot872480119:AAEbZ2Mom5PyyGrjmrMzG7j7HRguRi5YCRA/"


def get_updates_json(request):
    response = requests.get(request + 'getUpdates')
    return response.json()


def last_update(data):
    results = data['result']
    total_updates = len(results) - 1
    return results[total_updates]

print(get_updates_json(url))
