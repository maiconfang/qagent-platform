import subprocess


def run_tests():
    """
    Executes Playwright tests using subprocess.
    """

    try:
        process = subprocess.run(
            ["C:\\Program Files\\nodejs\\npx.cmd", "playwright", "test"],
            capture_output=True,
            text=True
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