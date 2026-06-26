from clients.windows_client import get_windows_metrics

def run():
    data = get_windows_metrics()
    mem = data.get("memory_percent", 0)

    return {
        "test": "MEMORY",
        "status": "PASS" if mem < 90 else "FAIL",
        "memory": mem
    }