def decide_next_step(analysis):
    """
    Decision logic based on failure type.
    """

    if analysis["status"] == "SUCCESS":
        return "STOP"

    failure_type = analysis.get("failure_type")

    if failure_type == "TIMEOUT":
        return "RETRY"

    if failure_type == "NETWORK_ERROR":
        return "RETRY"

    if failure_type == "ELEMENT_NOT_FOUND":
        return "STOP"

    if failure_type == "ASSERTION_FAILURE":
        return "STOP"

    return "STOP"