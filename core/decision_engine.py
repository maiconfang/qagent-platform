from core.flaky_detector import is_flaky


def decide_next_step(analysis, phase_name=None, failure_history=None, state=None):
    status = analysis.get("status")
    error_type = analysis.get("error_type")

    # 🔥 NEW: stability calculation (safe)

    avg_stability = 100

    if state and hasattr(state, "test_history"):
        test_histories = state.test_history.values()

        stability_scores = []

        for history in test_histories:
            total = len(history)
            success = history.count("SUCCESS")

            if total > 0:
                stability = (success / total) * 100
                stability_scores.append(stability)

        if stability_scores:
            avg_stability = sum(stability_scores) / len(stability_scores)

    # SUCCESS → continue normal execution
    if status == "SUCCESS":
        return {
            "action": "CONTINUE",
            "reason": f"{phase_name} execution succeeded"
        }

    # FAILURE → apply decision logic
    if status == "FAILURE":

        history = failure_history.get(phase_name, [])

        # 🔥 FLAKY DETECTION (NEW)
        if is_flaky(history):

            if avg_stability < 60:
                return {
                    "action": "RETRY",
                    "reason": f"{phase_name} shows critical flaky behavior (stability={avg_stability:.0f}%)"
                }

            elif avg_stability < 85:
                return {
                    "action": "RETRY",
                    "reason": f"{phase_name} shows moderate flaky behavior (stability={avg_stability:.0f}%)"
                }

            else:
                return {
                    "action": "CONTINUE",
                    "reason": f"{phase_name} flaky but stable overall (stability={avg_stability:.0f}%)"
                }

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
            if history and len(history) >= 2:
                return {
                    "action": "STOP",
                    "reason": f"{phase_name} assertion failed multiple times - stopping"
                }
            return {
                "action": "RETRY",
                "reason": f"{phase_name} assertion failed - retry triggered"
            }

        # Fallback (generic failure)
        if history and len(history) >= 2:
            return {
                "action": "STOP",
                "reason": f"{phase_name} failed multiple times - stopping"
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