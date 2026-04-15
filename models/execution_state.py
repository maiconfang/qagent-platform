# models/execution_state.py

class ExecutionState:
    def __init__(self, goal, project):
        self.goal = goal
        self.project = project

        # Failure tracking (per phase)
        self.failures = {}

        # Phase execution history (for flaky detection)
        self.phase_history = {}

        # Action tracking (future use)
        self.action_history = []
        self.last_action = None

    def record_failure(self, phase_name):
        self.failures[phase_name] = self.failures.get(phase_name, 0) + 1

    def record_phase_result(self, phase_name, status):
        if phase_name not in self.phase_history:
            self.phase_history[phase_name] = []
        self.phase_history[phase_name].append(status)

    def record_action(self, action):
        self.action_history.append(action)
        self.last_action = action

    def to_dict(self):
        return {
            "failures": self.failures,
            "phase_history": self.phase_history
        }

    def load_from_dict(self, data):
        self.failures = data.get("failures", {})
        self.phase_history = data.get("phase_history", {})        