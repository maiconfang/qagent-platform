def decide_next_step(analysis, phase_name=None, failure_history=None):
    status = analysis.get("status")

    # SUCCESS → continue normal execution
    if status == "SUCCESS":
        return {
            "action": "CONTINUE",
            "reason": f"{phase_name} execution succeeded"
        }

    # FAILURE → apply decision logic
    if status == "FAILURE":

        # If this phase already failed before → stop execution
        if failure_history and failure_history.get(phase_name, 0) >= 1:
            return {
                "action": "STOP",
                "reason": f"{phase_name} failed twice - stopping execution"
            }

        # If HIGH_IMPACT phase fails → stop immediately (critical)
        if phase_name == "HIGH_IMPACT":
            return {
                "action": "STOP",
                "reason": f"{phase_name} is critical - stopping execution"
            }

        # Otherwise → retry execution
        return {
            "action": "RETRY",
            "reason": f"{phase_name} execution failed - retry triggered"
        }

    # Fallback for unexpected states
    return {
        "action": "UNKNOWN",
        "reason": "Unexpected state"
    }