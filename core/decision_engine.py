def decide_next_step(analysis):
    """
    Decision logic based on failure type.
    """

    status = analysis.get("status")

    # ✅ SUCCESS → continue to next phase
    if status == "SUCCESS":
        return "CONTINUE"

    failure_type = analysis.get("failure_type")

    # 🔁 Retry scenarios
    if failure_type == "TIMEOUT":
        return "RETRY"

    if failure_type == "NETWORK_ERROR":
        return "RETRY"

    # 🛑 Stop scenarios (critical or functional failures)
    if failure_type == "ELEMENT_NOT_FOUND":
        return "STOP"

    if failure_type == "ASSERTION_FAILURE":
        return "STOP"

    # 🛑 Default fallback
    return "STOP"