class PhaseMetrics:
    def __init__(self, phase_name):
        self.phase = phase_name
        self.duration = 0
        self.total = 0
        self.passed = 0
        self.failed = 0

    def to_dict(self):
        return {
            "duration": self.duration,
            "tests": self.total,
            "passed": self.passed,
            "failed": self.failed
        }