import subprocess
from utils.logger import log

def run_tests():
    log("Running Playwright tests...")

    result = subprocess.run(
        ["npx", "playwright", "test"],
        capture_output=True,
        text=True
    )

    log("Tests finished")

    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode
    }
