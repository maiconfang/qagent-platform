import sys
from core.runner import run_tests
from core.analyzer import analyze_results
from core.reporter import generate_report
from core.decision_engine import decide_next_step

from dotenv import load_dotenv
import os

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

        log("Running tests...", f"{current_phase} | EXECUTION")
        result = run_tests(PHASES[current_phase])

        log("Analyzing results...", f"{current_phase} | ANALYSIS")
        analysis = analyze_results(result)

        log(f"Status: {analysis['status']}", f"{current_phase} | RESULT")

        decision = decide_next_step(analysis)
        log(f"Decision: {decision}", "DECISION")

        final_result = result
        final_analysis = analysis
        final_phase = current_phase
        final_decision = decision

        # ❌ STOP = failure scenario
        if decision == "STOP":
            break

        # =========================
        # EXTENDED PHASE
        # =========================
        current_phase = "EXTENDED"

        log("Running tests...", f"{current_phase} | EXECUTION")
        result = run_tests(PHASES[current_phase])

        log("Analyzing results...", f"{current_phase} | ANALYSIS")
        analysis = analyze_results(result)

        log(f"Status: {analysis['status']}", f"{current_phase} | RESULT")

        decision = decide_next_step(analysis)
        log(f"Decision: {decision}", "DECISION")

        final_result = result
        final_analysis = analysis
        final_phase = current_phase
        final_decision = decision

        # ❌ STOP = failure scenario
        if decision == "STOP":
            break

        # ✅ NEW: if everything passed, stop loop
        if decision == "CONTINUE":
             break

        # Only increment if execution continues
        attempt += 1

    # =========================
    # REPORT GENERATION
    # =========================
    log("Generating structured report...", "REPORT")

    # ✅ NEW: normalize final decision
    if final_analysis and final_analysis["status"] == "SUCCESS":
        final_decision = "DONE"

    report_data = {
        "command": user_input,
        "finalStatus": final_analysis["status"] if final_analysis else "UNKNOWN",
        "phase": final_phase,
        "attempts": attempt + 1,
        "decision": final_decision,
        "summary": {
            "failureType": final_analysis.get("failureType") if final_analysis else None,
            "message": final_analysis.get("message") if final_analysis else None
        }
    }

    generate_report(report_data)

    log("Done.", "END")


if __name__ == "__main__":
    main()