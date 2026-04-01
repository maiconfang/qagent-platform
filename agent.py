
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


def main():
    if len(sys.argv) < 2:
        print("Usage: python agent.py \"your command\"")
        return

    user_input = sys.argv[1]
    log(f"Received command: {user_input}", "INPUT")

    # Default project
    project_name = "taskmanagerplus"

    # Parse optional --project argument
    if "--project" in sys.argv:
        project_index = sys.argv.index("--project")
        if project_index + 1 < len(sys.argv):
            project_name = sys.argv[project_index + 1]

    log(f"Using project: {project_name}", "CONFIG")        

    config = load_config(project_name)
    if "phases" not in config:
        raise ValueError(f"Invalid config: 'phases' not found for project {project_name}")
    
    PHASES = config["phases"]

    max_attempts = int(os.getenv("MAX_ATTEMPTS", 2))
    attempt = 0
    failure_history = {}

    agent_timer = Timer()
    agent_timer.start()

    phases_metrics = {}
    execution_history = []

    final_result = None
    final_analysis = None
    final_phase = None
    final_decision = None

    while attempt < max_attempts:
        log(f"Execution attempt: {attempt + 1}", "LOOP")

        # =========================
        # HIGH IMPACT PHASE
        # =========================
        current_phase = "HIGH_IMPACT"

        phase_timer = Timer()
        phase_timer.start()

        log("Running tests...", f"{current_phase} | EXECUTION")
        result = run_tests(PHASES[current_phase])

        log("Analyzing results...", f"{current_phase} | ANALYSIS")
        analysis = analyze_results(result)

        if analysis["status"] != "SUCCESS":
            failure_history[current_phase] = failure_history.get(current_phase, 0) + 1

        phase_timer.stop()
        duration = phase_timer.duration()

        tests_count = len(PHASES[current_phase])
        passed = tests_count if analysis["status"] == "SUCCESS" else 0
        failed = tests_count if analysis["status"] != "SUCCESS" else 0

        phase_status = analysis["status"]

        phases_metrics[current_phase] = {
            "status": phase_status,
            "duration": duration,
            "tests": tests_count,
            "passed": passed,
            "failed": failed
        }

        execution_history.append({
            "phase": current_phase,
            "status": phase_status,
            "duration": duration
        })

        log(f"Status: {analysis['status']}", f"{current_phase} | RESULT")
        log(f"duration={duration}s tests={tests_count} passed={passed} failed={failed}", f"{current_phase} | METRICS")

        decision = decide_next_step(analysis)
        log(f"Decision: {decision} (status={analysis['status']})", "DECISION")

        final_result = result
        final_analysis = analysis
        final_phase = current_phase
        final_decision = decision

        if failure_history.get(current_phase, 0) >= 2:
            log(f"Repeated failure in {current_phase}, stopping retries", "INTELLIGENCE")
            final_decision = "STOP"
            break

        if decision == "STOP":
            log("Skipping remaining phases due to failure", "FLOW")
            break

        # =========================
        # EXTENDED PHASE
        # =========================
        current_phase = "EXTENDED"

        phase_timer = Timer()
        phase_timer.start()

        log("Running tests...", f"{current_phase} | EXECUTION")
        result = run_tests(PHASES[current_phase])

        log("Analyzing results...", f"{current_phase} | ANALYSIS")
        analysis = analyze_results(result)

        if analysis["status"] != "SUCCESS":
            failure_history[current_phase] = failure_history.get(current_phase, 0) + 1

        phase_timer.stop()
        duration = phase_timer.duration()

        tests_count = len(PHASES[current_phase])
        passed = tests_count if analysis["status"] == "SUCCESS" else 0
        failed = tests_count if analysis["status"] != "SUCCESS" else 0

        phase_status = analysis["status"]

        phases_metrics[current_phase] = {
            "status": phase_status,
            "duration": duration,
            "tests": tests_count,
            "passed": passed,
            "failed": failed
        }

        execution_history.append({
            "phase": current_phase,
            "status": phase_status,
            "duration": duration
        })

        log(f"Status: {analysis['status']}", f"{current_phase} | RESULT")
        log(f"duration={duration}s tests={tests_count} passed={passed} failed={failed}", f"{current_phase} | METRICS")

        decision = decide_next_step(analysis)
        log(f"Decision: {decision} (status={analysis['status']})", "DECISION")

        final_result = result
        final_analysis = analysis
        final_phase = current_phase
        final_decision = decision

        if failure_history.get(current_phase, 0) >= 2:
            log(f"Repeated failure in {current_phase}, stopping retries", "INTELLIGENCE")
            final_decision = "STOP"
            break

        if decision == "STOP":
            log("Skipping remaining phases due to failure", "FLOW")
            break

        if decision == "CONTINUE":
            log("Execution successful, stopping retries", "LOOP")
            break

        attempt += 1

    agent_timer.stop()
    total_duration = agent_timer.duration()

    log("Generating structured report...", "REPORT")

    if final_analysis and final_analysis["status"] == "SUCCESS":
        final_decision = "DONE"

    insights = []

    # Insight 1: HIGH_IMPACT stability check
    if phases_metrics.get("HIGH_IMPACT", {}).get("status") == "SUCCESS":
        insights.append("HIGH_IMPACT phase is stable")

    # Insight 2: EXTENDED execution time impact
    extended = phases_metrics.get("EXTENDED")
    if extended:
        insights.append(f"EXTENDED adds {extended['duration']}s to execution time")

    # Insight 3: total execution time
    insights.append(f"Total execution time: {total_duration}s")    

    report_data = {
        "command": user_input,
        "finalStatus": final_analysis["status"] if final_analysis else "UNKNOWN",
        "phase": final_phase,
        "attempts": attempt + 1,
        "decision": final_decision,
        "duration": total_duration,
        "phases": phases_metrics,
        "summary": {
            "failureType": final_analysis.get("failureType") if final_analysis else None,
            "message": final_analysis.get("message") if final_analysis else None
        },
        "history": execution_history,
        "insights": insights,
    }

    generate_report(report_data)

    log("Done.", "END")


if __name__ == "__main__":
    main()
