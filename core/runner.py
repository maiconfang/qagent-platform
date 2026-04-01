import subprocess
import os


def run_tests(test_list=None):
    """
    Executes Playwright tests using subprocess.
    Supports optional test file filtering.
    """

    test_project_path = os.getenv("TEST_PROJECT_PATH", ".")
    base_command = os.getenv("PLAYWRIGHT_COMMAND", "npx.cmd playwright test")

    command = base_command.split()

     # 👇 NEW: adds specific tests
    if test_list:
        command.extend(test_list)

    print(f"[AGENT] Running command: {' '.join(command)}")

    try:
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            cwd=test_project_path
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