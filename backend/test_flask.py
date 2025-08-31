import requests

new_task = {
    "machine": "windows",
    "data": [
            {"time": "2023-01-01T12:00:00Z", "keys": "a"},
            {"time": "2023-01-01T12:00:01Z", "keys": "b"}
    ]
}

# r = requests.post('http://127.0.0.1:5000/api/upload', json=new_task)
# print(r.status_code, r.text)   # should be 201 and the new task JSON

# r = requests.get('http://127.0.0.1:5000/api/getTargetMachinesList')
# print(r.status_code, r.text)   # should be 200 and include the new task

r = requests.get('http://127.0.0.1:5000/api/getData/windows')
print(r.json())   # should be 200 and include the new task