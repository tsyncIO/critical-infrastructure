from tests import test_cpu, test_memory, test_network, test_thermal, test_bmc
from logger import log
from config import ensure_dirs, REPORT_DIR
import json
import os

def run_all_tests():
    log("Starting OpenBMC Validation Lab")
    ensure_dirs()

    results = [
        test_cpu.run(),
        test_memory.run(),
        test_network.run(),
        test_thermal.run(),
        test_bmc.run(),
    ]

    report_path = os.path.join(REPORT_DIR, "report.json")
    with open(report_path, "w") as f:
        json.dump(results, f, indent=4)

    log(f"Test execution completed, report written to {report_path}")
    return results


if __name__ == "__main__":
    results = run_all_tests()

    print("\nFINAL REPORT:\n")
    for r in results:
        print(r)