import re


def analyze_results(result, json_data=None):
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
        "error_summary": None,
        "tests": []
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

    if json_data:
        analysis["tests"] = extract_tests_from_json(json_data)
    else:
        analysis["tests"] = extract_test_names(stdout)

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


def extract_test_names(stdout):
    tests = []

    for line in stdout.splitlines():
        line = line.strip()

        if not line:
            continue

        # Detect Playwright test result lines
        if "›" in line:
            parts = line.split("›")

            if len(parts) >= 2:
                test_name = parts[-1].strip()
                tests.append(test_name)

    # Remove duplicates while preserving order
    return list(dict.fromkeys(tests))


def classify_error(error_message):
    if not error_message:
        return None

    msg = error_message.lower()

    if "timeout" in msg:
        return "UI_TIMEOUT"

    if "locator" in msg or "element not found" in msg:
        return "LOCATOR_FAILURE"

    if "expect" in msg or "assert" in msg:
        return "ASSERTION_FAILURE"

    if "403" in msg:
        return "AUTH_FAILURE"

    if "404" in msg:
        return "RESOURCE_NOT_FOUND"

    if "400" in msg:
        return "VALIDATION_ERROR"

    return "UNKNOWN_ERROR"




def extract_tests_from_json(data):
    tests = []

    for suite in data.get("suites", []):
        for inner_suite in suite.get("suites", []):
            for spec in inner_suite.get("specs", []):
                test_name = spec.get("title")

                for test in spec.get("tests", []):
                    results = test.get("results", [])
                    if not results:
                        continue

                    result = results[0]

                    status = result.get("status")
                    duration = result.get("duration", 0)

                    # 👇 pegar erro (se existir)
                    error_obj = result.get("error")

                    error_message = None
                    if isinstance(error_obj, dict):
                        error_message = error_obj.get("message") or str(error_obj)
                    
                    error_type = classify_error(error_message)

                    tests.append({
                        "name": test_name,
                        "status": status,
                        "duration": duration,
                        "error": error_message,
                        "error_type": error_type
                    })

    return tests