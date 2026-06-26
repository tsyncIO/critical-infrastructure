from clients.windows_client import get_windows_metrics

def run():
    data = get_windows_metrics()

    return {
        "test": "THERMAL_SIM",
        "status": "OK",
        "cpu_temp_proxy": data["cpu_percent"]
    }