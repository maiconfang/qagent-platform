
import sys
import os
from dotenv import load_dotenv

from core.runner import run_tests
from core.analyzer import analyze_results
from core.reporter import generate_report
from core.decision_engine import decide_next_step

from utils.timer import Timer

load_dotenv()


def log(message, context=None):
    if context:
        print(f"[AGENT][{context}] {message}")
    else:
        print(f"[AGENT] {message}")


# Define execution phases (system configuration)
PHASES = {
    "HIGH_IMPACT": [
        "tests/province/province.form.validation.spec.ts",
        "tests/province/province.create.api.spec.ts",
        "tests/province/province.edit.api.spec.ts"
    ],
    "EXTENDED": [
        "tests/province/province.menu.navigation.spec.ts",
        "tests/province/province.search.empty-state.spec.ts"
    ],
    "FULL": [
        "tests/province/province.delete.api.spec.ts",
        "tests/province/province-ui-legacy.spec.ts"
    ]
}


def main():
    if len(sys.argv) < 2:
        print("Usage: python agent.py \"your command\"")
        return

    user_input = sys.argv[1]
    log(f"Received command: {user_input}", "INPUT")

    max_attempts = int(os.getenv("MAX_ATTEMPTS", 2))
    attempt = 0
    failure_history = {}

    agent_timer = Timer()
    agent_timer.start()

    phases_metrics = {}

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

        phases_metrics[current_phase] = {
            "duration": duration,
            "tests": tests_count,
            "passed": passed,
            "failed": failed
        }

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

        phases_metrics[current_phase] = {
            "duration": duration,
            "tests": tests_count,
            "passed": passed,
            "failed": failed
        }

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
        }
    }

    generate_report(report_data)

    log("Done.", "END")


if __name__ == "__main__":
    main()
