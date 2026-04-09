import sys
import os
from dotenv import load_dotenv

from core.runner import run_tests
from core.analyzer import analyze_results
from core.reporter import generate_report
from core.decision_engine import decide_next_step

from utils.timer import Timer
from utils.config_loader import load_config

load_dotenv()


def log(message, context=None):
    if context:
        print(f"[AGENT][{context}] {message}")
    else:
        print(f"[AGENT] {message}")


def execute_phase(phase_name, phase_tests, state, failure_history):
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

    return result, analysis, metrics, history_entry, decision


def main():

    if len(sys.argv) < 2:
        print("Usage: python agent.py \"your command\"")
        return

    user_input = sys.argv[1]
    log(f"Received command: {user_input}", "INPUT")

    parts = user_input.lower().split()
    domain = parts[1] if len(parts) >= 2 else None

    log(f"Detected domain: {domain}", "DOMAIN")

    project_name = "taskmanagerplus"

    if "--project" in sys.argv:
        project_index = sys.argv.index("--project")
        if project_index + 1 < len(sys.argv):
            project_name = sys.argv[project_index + 1]

    log(f"Using project: {project_name}", "CONFIG")

    config = load_config(project_name)

    if "domains" not in config:
        raise ValueError(f"Invalid config: 'domains' not found for project {project_name}")

    domains = config.get("domains", {})

    if not domain or domain not in domains:
        raise ValueError(f"Domain '{domain}' not found in config")

    PHASES = domains[domain]["phases"]

    max_attempts = int(os.getenv("MAX_ATTEMPTS", 2))
    attempt = 0
    failure_history = {}

    state = {
        "command": user_input,
        "project": project_name,
        "domain": domain,
        "current_phase": None,
        "attempt": attempt,
        "max_attempts": max_attempts,
        "history": [],
        "failures": {},
        "last_decision": None
    }

    agent_timer = Timer()
    agent_timer.start()

    phases_metrics = {}
    execution_history = []

    final_analysis = None
    final_phase = None
    final_decision = None

    try:
        while attempt < max_attempts:
            log(f"Execution attempt: {attempt + 1}", "LOOP")

            for phase_name, phase_tests in PHASES.items():
                state["current_phase"] = phase_name

                result, analysis, metrics, history_entry, decision = execute_phase(
                    phase_name,
                    phase_tests,
                    state,
                    failure_history
                )

                phases_metrics[phase_name] = metrics
                execution_history.append(history_entry)

                state["last_decision"] = decision

                log(f"Decision: {decision}", "DECISION")

                final_analysis = analysis
                final_phase = phase_name
                final_decision = decision

                if failure_history.get(phase_name, 0) >= 2:
                    final_decision = "STOP"
                    break

                if decision == "STOP":
                    break

            break

    finally:
        agent_timer.stop()
        total_duration = agent_timer.duration()

        log("Generating structured report...", "REPORT")

        if final_analysis and final_analysis["status"] == "SUCCESS":
            final_decision = "DONE"

        report_data = {
            "command": user_input,
            "finalStatus": final_analysis["status"] if final_analysis else "UNKNOWN",
            "phase": final_phase,
            "attempts": attempt + 1,
            "decision": final_decision,
            "duration": total_duration,
            "phases": phases_metrics,
            "history": execution_history,
        }

        insights = []

        if phases_metrics.get("HIGH_IMPACT", {}).get("status") == "SUCCESS":
            insights.append("HIGH_IMPACT phase is stable")

        extended = phases_metrics.get("EXTENDED")
        if extended:
            insights.append(f"EXTENDED phase added {extended['duration']}s to execution time")

        insights.append(f"Total execution time: {total_duration}s")

        if any(h["status"] == "FAILURE" for h in execution_history):
            insights.append("Potential flaky behavior detected")

        report_data["insights"] = insights

        generate_report(report_data)

        log("Done.", "END")


if __name__ == "__main__":
    main()
