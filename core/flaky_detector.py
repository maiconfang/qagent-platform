# core/flaky_detector.py

"""
Flaky Detector - QAgent Platform

This module simulates how a QA Engineer identifies unstable tests.

It analyzes execution history to detect flaky behavior,
where the same test produces inconsistent results
across multiple executions.

The detector helps the platform:
- Avoid false negatives
- Apply smarter retries
- Improve execution reliability
"""

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