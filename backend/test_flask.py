import requests

new_task = {
    "machine": "mac",
    "data": [
            {"time": "2023-01-01T12:00:00Z", "keys": "a"},
            {"time": "2023-01-01T12:00:01Z", "keys": "b"}
    ]
}

r = requests.post('http://127.0.0.1:5000/api/upload', json=new_task)
print(r.status_code, r.text)   # should be 201 and the new task JSON

# r = requests.get('http://127.0.0.1:5000/api/upload')
# print(r.status_code, r.text)   # should be 200 and include the new task