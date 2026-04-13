def decide_next_step(analysis, phase_name=None, failure_history=None):
    status = analysis.get("status")
    error_type = analysis.get("error_type")

    # SUCCESS → continue normal execution
    if status == "SUCCESS":
        return {
            "action": "CONTINUE",
            "reason": f"{phase_name} execution succeeded"
        }

    # FAILURE → apply decision logic
    if status == "FAILURE":

        # 🔥 HIGH_IMPACT should always stop immediately (critical phase)
        if phase_name == "HIGH_IMPACT":
            return {
                "action": "STOP",
                "reason": f"{phase_name} is critical - stopping execution"
            }

        # API errors → stop immediately
        if error_type == "API":
            return {
                "action": "STOP",
                "reason": f"{phase_name} failed due to API error"
            }

        # Timeout → retry (can be flaky)
        if error_type == "TIMEOUT":
            return {
                "action": "RETRY",
                "reason": f"{phase_name} timeout detected - retry triggered"
            }

        # Locator → likely test issue → stop
        if error_type == "LOCATOR":
            return {
                "action": "STOP",
                "reason": f"{phase_name} locator issue detected"
            }

        # Assertion → retry once, then stop
        if error_type == "ASSERTION":
            if failure_history and failure_history.get(phase_name, 0) >= 1:
                return {
                    "action": "STOP",
                    "reason": f"{phase_name} assertion failed twice - stopping"
                }
            return {
                "action": "RETRY",
                "reason": f"{phase_name} assertion failed - retry triggered"
            }

        # Fallback (generic failure)
        if failure_history and failure_history.get(phase_name, 0) >= 1:
            return {
                "action": "STOP",
                "reason": f"{phase_name} failed twice - stopping"
            }

        return {
            "action": "RETRY",
            "reason": f"{phase_name} execution failed - retry triggered"
        }
    

    # Fallback for unexpected states
    return {
        "action": "UNKNOWN",
        "reason": "Unexpected state"
    }