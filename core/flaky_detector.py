# core/flaky_detector.py

def is_flaky(history):
    """
    Detects flaky behavior based on status history.
    Example:
        ["SUCCESS", "FAILURE"] → True
        ["SUCCESS", "SUCCESS"] → False
    """

    if not history or len(history) < 2:
        return False

    return len(set(history)) > 1