import threading
import time
import urllib.request
import json
import uvicorn
from app.main import app

def run_server():
    uvicorn.run(app, host="127.0.0.1", port=8888, log_level="warning")

server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()
time.sleep(2)

try:
    with urllib.request.urlopen("http://127.0.0.1:8888/api/v1/health") as response:
        data = json.loads(response.read().decode())
        print("PROBE_SUCCESS:", response.status, data)
except Exception as e:
    print("PROBE_ERROR:", e)
