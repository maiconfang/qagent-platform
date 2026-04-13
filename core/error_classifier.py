def classify_error(result):
    """
    Classify error based on stderr/stdout patterns.
    """

    output = (result.get("stdout", "") + result.get("stderr", "")).lower()

    # Timeout errors
    if "timeout" in output:
        return "TIMEOUT"

    # Locator / element not found
    if "not found" in output or "locator" in output or "element" in output:
        return "LOCATOR"

    # API errors
    if "500" in output or "api" in output or "response" in output:
        return "API"

    return "UNKNOWN"