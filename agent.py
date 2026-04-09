import sys
import os
from dotenv import load_dotenv

from core.runner import run_tests
from core.analyzer import analyze_results
from core.reporter import generate_report
from core.decision_engine import decide_next_step

from utils.timer import Timer
from utils.config_loader import load_config
from models.execution_result import ExecutionResult

load_dotenv()


# =========================
# LOGGER
# =========================
def log(message, context=None):
    if context:
        print(f"[AGENT][{context}] {message}")
    else:
        print(f"[AGENT] {message}")



# =========================
# AGENT
# =========================
class Agent:

    def __init__(self):
        self.max_attempts = int(os.getenv("MAX_ATTEMPTS", 2))

    def extract_domain(self, user_input: str) -> str:
        parts = user_input.lower().split()
        return parts[1] if len(parts) >= 2 else None

    def resolve_project_config(self):
        project_name = "taskmanagerplus"

        if "--project" in sys.argv:
            project_index = sys.argv.index("--project")
            if project_index + 1 < len(sys.argv):
                project_name = sys.argv[project_index + 1]

        log(f"Using project: {project_name}", "CONFIG")

        config = load_config(project_name)

        if "domains" not in config:
            raise ValueError(f"Invalid config: 'domains' not found for project {project_name}")

        return project_name, config

    def execute_phase(self, phase_name, phase_tests, failure_history):
        phase_timer = Timer()
        phase_timer.start()

        log("Running tests...", f"{phase_name} | EXECUTION")
        result = run_tests(phase_tests)

        log("Analyzing results...", f"{phase_name} | ANALYSIS")
        analysis = analyze_results(result)

        if analysis["status"] != "SUCCESS":
            failure_history[phase_name] = failure_history.get(phase_name, 0) + 1

        phase_timer.stop()
        duration = phase_timer.duration()

        tests_count = len(phase_tests)
        passed = tests_count if analysis["status"] == "SUCCESS" else 0
        failed = tests_count if analysis["status"] != "SUCCESS" else 0

        metrics = {
            "status": analysis["status"],
            "duration": duration,
            "tests": tests_count,
            "passed": passed,
            "failed": failed
        }

        history_entry = {
            "phase": phase_name,
            "status": analysis["status"],
            "duration": duration
        }

        decision = decide_next_step(analysis)

        return metrics, history_entry, analysis, decision

    def run(self, user_input: str):

        log(f"Received command: {user_input}", "INPUT")

        domain = self.extract_domain(user_input)
        log(f"Detected domain: {domain}", "DOMAIN")

        project_name, config = self.resolve_project_config()

        domains = config.get("domains", {})

        if not domain or domain not in domains:
            raise ValueError(f"Domain '{domain}' not found in config")

        phases = domains[domain]["phases"]

        execution_result = ExecutionResult(user_input)

        agent_timer = Timer()
        agent_timer.start()

        failure_history = {}

        try:
            for phase_name, phase_tests in phases.items():

                metrics, history_entry, analysis, decision = self.execute_phase(
                    phase_name,
                    phase_tests,
                    failure_history
                )

                execution_result.update_phase(
                    phase_name,
                    metrics,
                    history_entry,
                    analysis,
                    decision
                )

                log(f"Decision: {decision}", "DECISION")

                if failure_history.get(phase_name, 0) >= 2 or decision == "STOP":
                    break

        finally:
            agent_timer.stop()
            execution_result.duration = agent_timer.duration()

            log("Generating structured report...", "REPORT")

            if execution_result.final_analysis and execution_result.final_analysis["status"] == "SUCCESS":
                execution_result.final_decision = "DONE"

            report_data = self.build_report(execution_result)

            generate_report(report_data)

            log("Done.", "END")

    def build_report(self, result: ExecutionResult):

        report_data = {
            "command": result.command,
            "finalStatus": result.final_analysis["status"] if result.final_analysis else "UNKNOWN",
            "phase": result.final_phase,
            "decision": result.final_decision,
            "duration": result.duration,
            "phases": result.phases_metrics,
            "history": result.execution_history,
        }

        insights = []

        if result.phases_metrics.get("HIGH_IMPACT", {}).get("status") == "SUCCESS":
            insights.append("HIGH_IMPACT phase is stable")

        extended = result.phases_metrics.get("EXTENDED")
        if extended:
            insights.append(f"EXTENDED phase added {extended['duration']}s to execution time")

        insights.append(f"Total execution time: {result.duration}s")

        if any(h["status"] == "FAILURE" for h in result.execution_history):
            insights.append("Potential flaky behavior detected")

        report_data["insights"] = insights

        return report_data


# =========================
# ENTRY POINT
# =========================
def main():
    if len(sys.argv) < 2:
        print("Usage: python agent.py \"your command\"")
        return

    user_input = sys.argv[1]

    agent = Agent()
    agent.run(user_input)


if __name__ == "__main__":
    main()
