
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

    # -------------------------
    # DOMAIN
    # -------------------------
    parts = user_input.lower().split()
    domain = parts[1] if len(parts) >= 2 else None

    log(f"Detected domain: {domain}", "DOMAIN")

    # -------------------------
    # PROJECT
    # -------------------------
    project_name = "taskmanagerplus"

    if "--project" in sys.argv:
        project_index = sys.argv.index("--project")
        if project_index + 1 < len(sys.argv):
            project_name = sys.argv[project_index + 1]

    log(f"Using project: {project_name}", "CONFIG")

    # -------------------------
    # CONFIG
    # -------------------------
    config = load_config(project_name)

    if "domains" not in config:
        raise ValueError(f"Invalid config: 'domains' not found for project {project_name}")

    domains = config.get("domains", {})

    if not domain or domain not in domains:
        raise ValueError(f"Domain '{domain}' not found in config")

    PHASES = domains[domain]["phases"]

    # -------------------------
    # EXECUTION CONFIG
    # -------------------------
    max_attempts = int(os.getenv("MAX_ATTEMPTS", 2))
    attempt = 0
    failure_history = {}

    # ✅ STATE in the correct place
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

    # -------------------------
    # TIMERS
    # -------------------------
    agent_timer = Timer()
    agent_timer.start()

    phases_metrics = {}
    execution_history = []

    final_result = None
    final_analysis = None
    final_phase = None
    final_decision = None

    try:
        while attempt < max_attempts:
            log(f"Execution attempt: {attempt + 1}", "LOOP")

            # =========================
            # HIGH_IMPACT
            # =========================
            current_phase = "HIGH_IMPACT"
            state["current_phase"] = current_phase

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
                "status": analysis["status"],
                "duration": duration,
                "tests": tests_count,
                "passed": passed,
                "failed": failed
            }

            execution_history.append({
                "phase": current_phase,
                "status": analysis["status"],
                "duration": duration
            })

            decision = decide_next_step(analysis)
            state["last_decision"] = decision

            log(f"Decision: {decision}", "DECISION")

            final_result = result
            final_analysis = analysis
            final_phase = current_phase
            final_decision = decision

            if failure_history.get(current_phase, 0) >= 2:
                final_decision = "STOP"
                break

            if decision == "STOP":
                break

            # =========================
            # EXTENDED
            # =========================
            current_phase = "EXTENDED"
            state["current_phase"] = current_phase

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
                "status": analysis["status"],
                "duration": duration,
                "tests": tests_count,
                "passed": passed,
                "failed": failed
            }

            execution_history.append({
                "phase": current_phase,
                "status": analysis["status"],
                "duration": duration
            })

            decision = decide_next_step(analysis)
            state["last_decision"] = decision

            final_result = result
            final_analysis = analysis
            final_phase = current_phase
            final_decision = decision

            if failure_history.get(current_phase, 0) >= 2:
                final_decision = "STOP"
                break

            if decision == "STOP":
                break

            if decision == "CONTINUE":
                break

            attempt += 1
            state["attempt"] = attempt

    finally:
        # 🔒 GUARANTEED FINALIZATION (ANTI-BUG)
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
        
        # 🔍 EXTENDED instability detection
        extended_failures = [
            h for h in execution_history
            if h["phase"] == "EXTENDED" and h["status"] == "FAILURE"
        ]

        # 🔥 Smarter flaky detection (no duplication)
        if extended_failures:
            insights.append("Flaky behavior detected in EXTENDED phase")
        elif any(h["status"] == "FAILURE" for h in execution_history):
            insights.append("Potential flaky behavior detected")

        report_data["insights"] = insights

        assert "insights" in report_data, "Insights not generated!"

        generate_report(report_data)

        log("Done.", "END")


if __name__ == "__main__":
    main()
