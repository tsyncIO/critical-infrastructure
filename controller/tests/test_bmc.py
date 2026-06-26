from clients.openbmc_client import get_system_info


def run():
    data = get_system_info()
    status = "PASS"

    if isinstance(data, dict) and data.get("error"):
        status = "FAIL"
    elif "@odata.type" not in data:
        status = "FAIL"

    return {
        "test": "BMC_REDFISH",
        "status": status,
        "details": data
    }
