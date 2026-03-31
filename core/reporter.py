import os
from datetime import datetime


def generate_report(command, analysis, result):
    """
    Generates a simple text report.
    """

    os.makedirs("reports", exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_path = f"reports/report_{timestamp}.txt"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write("=== QAgent Report ===\n\n")

        f.write(f"Command: {command}\n")
        f.write(f"Status: {analysis['status']}\n")

        if analysis["status"] == "FAILURE":
            f.write(f"Failure Type: {analysis['failure_type']}\n")
            f.write(f"Failed Tests: {analysis['failed_tests']}\n")
            f.write(f"Error Summary: {analysis['error_summary']}\n")

        f.write("\n--- STDOUT ---\n")
        f.write(result.get("stdout", "")[:1000])

        f.write("\n\n--- STDERR ---\n")
        f.write(result.get("stderr", "")[:1000])

    print(f"[REPORT] Saved to {file_path}")