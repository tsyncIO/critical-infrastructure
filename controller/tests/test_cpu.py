from clients.windows_client import get_windows_metrics
from logger import log

def run():
    log("Running CPU test")

    data = get_windows_metrics()
    cpu = data.get("cpu_percent", 0)

    if cpu < 90:
        return {"test": "CPU", "status": "PASS", "cpu": cpu}
    else:
        return {"test": "CPU", "status": "FAIL", "cpu": cpu}