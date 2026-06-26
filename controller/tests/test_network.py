import os

def run():
    result = os.system("ping -c 2 8.8.8.8")

    return {
        "test": "NETWORK",
        "status": "PASS" if result == 0 else "FAIL"
    }