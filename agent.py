import sys
from core.runner import run_tests
from core.analyzer import analyze_results
from core.reporter import generate_report
from core.decision_engine import decide_next_step


def log(message):
    print(f"[AGENT] {message}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python agent.py \"your command\"")
        return

    user_input = sys.argv[1]
    log(f"Received command: {user_input}")

    max_attempts = 2
    attempt = 0

    final_result = None
    final_analysis = None

    while attempt < max_attempts:
        log(f"Execution attempt: {attempt + 1}")

        log("Starting test execution...")
        result = run_tests()

        log("Analyzing results...")
        analysis = analyze_results(result)

        log(f"Analysis complete: {analysis['status']}")

        decision = decide_next_step(analysis)

        log(f"Decision: {decision}")

        final_result = result
        final_analysis = analysis

        if decision == "STOP":
            break

        attempt += 1

    log("Generating report...")
    generate_report(user_input, final_analysis, final_result)

    log("Done.")


if __name__ == "__main__":
    main()