import os
from datetime import datetime
import json


def generate_report(*args):
    """
    Supports both:
    - Old format: (command, analysis, result)
    - New format: (report_data dict)
    """

    os.makedirs("reports", exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # =========================
    # NEW STRUCTURED FORMAT
    # =========================
    if len(args) == 1 and isinstance(args[0], dict):
        report_data = args[0]

        file_path = f"reports/report_{timestamp}.json"

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2)

        print(f"[REPORT] Saved to {file_path}")
        return

    # =========================
    # LEGACY FORMAT (your current)
    # =========================
    elif len(args) == 3:
        command, analysis, result = args

        file_path = f"reports/report_{timestamp}.txt"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write("=== QAgent Report ===\n\n")

            f.write(f"Command: {command}\n")
            f.write(f"Status: {analysis['status']}\n")

            if analysis["status"] == "FAILURE":
                f.write(f"Failure Type: {analysis.get('failure_type')}\n")
                f.write(f"Failed Tests: {analysis.get('failed_tests')}\n")
                f.write(f"Error Summary: {analysis.get('error_summary')}\n")

            f.write("\n--- STDOUT ---\n")
            f.write(result.get("stdout", "")[:1000])

            f.write("\n\n--- STDERR ---\n")
            f.write(result.get("stderr", "")[:1000])

        print(f"[REPORT] Saved to {file_path}")
        return

    else:
        raise ValueError("Invalid arguments passed to generate_report()")