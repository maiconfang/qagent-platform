from utils.logger import log

def analyze_results(test_results):
    log("Analyzing test results...")

    if test_results["returncode"] == 0:
        status = "SUCCESS"
    else:
        status = "FAILURE"

    return {
        "status": status,
        "details": test_results["stdout"][:500]
    }
