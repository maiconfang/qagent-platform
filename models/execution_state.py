# models/execution_state.py

class ExecutionState:
    def __init__(self, goal, project):
        self.goal = goal
        self.project = project
        self.failures = {}        # failures per phase
        self.history = []         # actions taken
        self.last_action = None

    def record_failure(self, phase_name):
        self.failures[phase_name] = self.failures.get(phase_name, 0) + 1

    def record_action(self, action):
        self.history.append(action)
        self.last_action = action