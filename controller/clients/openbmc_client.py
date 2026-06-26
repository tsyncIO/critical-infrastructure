import requests
from config import OPENBMC_HOST

def get_system_info():
    try:
        r = requests.get(OPENBMC_HOST + "/redfish/v1/")
        return r.json()
    except Exception as e:
        return {"error": str(e)}