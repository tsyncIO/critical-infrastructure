import requests
from config import WINDOWS_HOST

def get_windows_metrics():
    r = requests.get(WINDOWS_HOST + "/metrics")
    data = r.json()
    print(f"[DEBUG] windows metrics request -> {data}")
    return data

def health_check():
    r = requests.get(WINDOWS_HOST + "/health")
    data = r.json()
    print(f"[DEBUG] windows health request -> {data}")
    return data