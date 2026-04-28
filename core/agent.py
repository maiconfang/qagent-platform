# core/agent.py

import sys
import os
import json
from core.runner import run_tests
from core.analyzer import analyze_results
from core.reporter import generate_report
from core.decision_engine import decide_next_step

from utils.timer import Timer
from utils.config_loader import load_config
from models.execution_result import ExecutionResult
from models.phase_result import PhaseResult
from models.execution_state import ExecutionState

from utils.state_store import load_state, save_state
from core.html_reporter import generate_html_report

from dotenv import load_dotenv
load_dotenv()

PLAYWRIGHT_JSON_PATH = "../taskmanagerplus-tests/ui-tests/reports/ui/playwright-report.json"
THRESHOLD_SLOW_MS = int(os.getenv("SLOW_TEST_THRESHOLD", "5000"))


def log(message, context=None):
    if context:
        print(f"[AGENT][{context}] {message}")
    else:
        print(f"[AGENT] {message}")


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

    def execute_phase(self, phase_name, phase_tests, state):    
        phase_timer = Timer()
        phase_timer.start()

        log("Running tests...", f"{phase_name} | EXECUTION")
        result = run_tests(phase_tests)

        log("Analyzing results...", f"{phase_name} | ANALYSIS")
        json_data = None

        if os.path.exists(PLAYWRIGHT_JSON_PATH):
            try:
                with open(PLAYWRIGHT_JSON_PATH, "r", encoding="utf-8") as f:
                    json_data = json.load(f)
            except Exception as e:
                print("[WARNING] Failed to read Playwright JSON:", e)

        analysis = analyze_results(result, json_data)

        print("[DEBUG] tests:", analysis.get("tests"))

        for test in analysis.get("tests", []):
            test_name = test["name"]
            raw_status = test["status"]

            if raw_status == "passed":
                test_status = "SUCCESS"
            else:
                test_status = "FAILURE"

            state.record_test_result(test_name, test_status)

        # Flaky tracking
        state.record_phase_result(phase_name, analysis["status"])

        if analysis["status"] != "SUCCESS":
            state.record_failure(phase_name)

        phase_timer.stop()
        duration = phase_timer.duration()

        tests_count = len(phase_tests)
        passed = tests_count if analysis["status"] == "SUCCESS" else 0
        failed = tests_count if analysis["status"] != "SUCCESS" else 0

        phase_result = PhaseResult(
            name=phase_name,
            status=analysis["status"],
            duration=duration,
            tests=tests_count,
            passed=passed,
            failed=failed
        )
        decision = decide_next_step(
            analysis,
            phase_name=phase_name,
            failure_history=state.phase_history
        )

        return phase_result, analysis, decision

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
        state = ExecutionState(goal=user_input, project=project_name)

        persisted = load_state()
        state.load_from_dict(persisted)

        agent_timer = Timer()
        agent_timer.start()


        try:
            for phase_name, phase_tests in phases.items():

                phase_result, analysis, decision = self.execute_phase(
                    phase_name,
                    phase_tests,
                    state
                )

                execution_result.update_phase(
                    phase_name,
                    phase_result.to_metrics(),
                    phase_result.to_history_entry(),
                    analysis,
                    decision
                )

                log(f"Phase history: {state.phase_history}", "DEBUG")

                log(
                    f"Decision: {decision['action']} ({decision['reason']}) | Error: {analysis.get('error_type')}",
                    "DECISION"
                )

                if state.failures.get(phase_name, 0) >= 2 or decision["action"] == "STOP":    
                    break

        finally:
            agent_timer.stop()
            execution_result.duration = agent_timer.duration()

            log("Generating structured report...", "REPORT")

            if execution_result.final_analysis and execution_result.final_analysis["status"] == "SUCCESS":
                execution_result.final_decision = "DONE"

            report_data = self.build_report(execution_result, state)

            generate_report(report_data)
            generate_html_report(report_data)

            # 👇 persist state
            save_state(state.to_dict())
            log("Done.", "END")

    def build_report(self, result: ExecutionResult, state: ExecutionState):
        report_data = {
            "command": result.command,
            "finalStatus": result.final_analysis["status"] if result.final_analysis else "UNKNOWN",
            "phase": result.final_phase,
            "decision": result.final_decision,
            "duration": result.duration,
            "phases": result.phases_metrics,
            "history": result.execution_history,
            "tests": result.final_analysis.get("tests", []) if result.final_analysis else [],
        }

        insights = []

        is_flaky = any(len(set(h)) > 1 for h in state.phase_history.values())

        if not is_flaky and result.phases_metrics.get("HIGH_IMPACT", {}).get("status") == "SUCCESS":
            insights.append("HIGH_IMPACT phase is stable")

        extended = result.phases_metrics.get("EXTENDED")
        if extended:
            insights.append(f"EXTENDED phase added {extended['duration']}s to execution time")

        insights.append(f"Total execution time: {result.duration}s")

        phase_history_map = state.phase_history

        # Detect flaky behavior
        for phase_name, history in phase_history_map.items():
            if history and len(set(history)) > 1:
                history_str = " → ".join(history)

                insights.append(
                    f"FLAKY DETECTED: {phase_name} alternates between SUCCESS and FAILURE "
                    f"(history={history_str})"
                )

                insights.append(
                    f"Adaptive decision applied: RETRY instead of STOP for {phase_name}"
                )

        for test_name, history in state.test_history.items():
            if len(set(history)) > 1:
                history_str = " → ".join(history)

                insights.append(
                    f"FLAKY TEST DETECTED: {test_name} "
                    f"(history={history_str})"
                )

            # 🔥 NEW: Stability Score    
            total = len(history)
            success = history.count("SUCCESS")

            stability = (success / total) * 100 if total > 0 else 0

            if total >= 2:   
                insights.append(
                    f"STABILITY: {test_name} → {stability:.0f}% stable"
                )
                
        # 🔥 NEW: Slow test detection
        for test in (result.final_analysis or {}).get("tests", []):
            duration = test.get("duration", 0)

            if duration > THRESHOLD_SLOW_MS:
                insights.append(
                    f"SLOW TEST DETECTED: {test['name']} took {duration}ms"
                )                 

        report_data["insights"] = insights

        return report_data