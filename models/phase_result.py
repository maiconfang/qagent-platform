# models/phase_result.py

class PhaseResult:
    def __init__(self, name, status, duration, tests, passed, failed):
        self.name = name
        self.status = status
        self.duration = duration
        self.tests = tests
        self.passed = passed
        self.failed = failed

    def to_metrics(self):
        return {
            "status": self.status,
            "duration": self.duration,
            "tests": self.tests,
            "passed": self.passed,
            "failed": self.failed
        }

    def to_history_entry(self):
        return {
            "phase": self.name,
            "status": self.status,
            "duration": self.duration
        }