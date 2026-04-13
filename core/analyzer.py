import re


def analyze_results(result):
    """
    Enhanced analyzer with basic failure classification.
    """

    return_code = result["returncode"]
    stdout = result.get("stdout", "")
    stderr = result.get("stderr", "")

    analysis = {
        "status": "SUCCESS" if return_code == 0 else "FAILURE",
        "error_type": None,
        "failed_tests": 0,
        "error_summary": None
    }

    if return_code != 0:
        failure_type = detect_failure_type(stdout, stderr)
        failed_tests = extract_failed_tests(stdout)
        error_summary = extract_error_summary(stderr or stdout)

        analysis.update({
            "error_type": failure_type,
            "failed_tests": failed_tests,
            "error_summary": error_summary
        })

    return analysis


def detect_failure_type(stdout, stderr):
    combined = (stdout + stderr).lower()

    if "timeout" in combined:
        return "TIMEOUT"

    if "locator" in combined or "element not found" in combined:
        return "LOCATOR"

    if "expect" in combined:
        return "ASSERTION"

    if "net::err" in combined or "failed to fetch" in combined:
        return "API"

    if "winerror 2" in combined or "cannot find the file" in combined:
        return "ENVIRONMENT"

    return "UNKNOWN"


def extract_failed_tests(stdout):
    match = re.search(r"(\d+)\s+failed", stdout.lower())
    if match:
        return int(match.group(1))
    return 0


def extract_error_summary(output):
    lines = output.splitlines()

    for line in lines:
        if "error" in line.lower() or "timeout" in line.lower():
            return line.strip()

    return lines[-1] if lines else "No error summary available"