class ExecutionResult:
    def __init__(self, command):
        self.command = command
        self.phases_metrics = {}
        self.execution_history = []
        self.final_analysis = None
        self.final_phase = None
        self.final_decision = None
        self.duration = 0

    def update_phase(self, phase_name, metrics, history_entry, analysis, decision):
        self.phases_metrics[phase_name] = metrics
        self.execution_history.append(history_entry)
        self.final_analysis = analysis
        self.final_phase = phase_name
        self.final_decision = decision