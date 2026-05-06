import subprocess
import os

"""
Test Runner - QAgent Platform

This module simulates how a QA Engineer triggers
and monitors automated test execution.

It is responsible for:
- Running Playwright tests
- Capturing execution output
- Detecting execution failures
- Returning structured execution data

The runner is the entry point of the intelligent
QA execution pipeline.
"""

def run_tests(test_list=None):
    test_project_path = os.getenv("TEST_PROJECT_PATH", ".")
    base_command = os.getenv("PLAYWRIGHT_COMMAND", "npx.cmd playwright test")

    command = base_command.split()

    if test_list:
        command.extend(test_list)

    print(f"[AGENT] Running command: {' '.join(command)}")

    try:
        process = subprocess.run(
            " ".join(command),
            cwd=test_project_path,
            shell=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )

        return {
            "returncode": process.returncode,
            "stdout": process.stdout,
            "stderr": process.stderr
        }

    except Exception as e:
        return {
            "returncode": -1,
            "stdout": "",
            "stderr": str(e)
        }