import os
from datetime import datetime

def generate_report(user_input, analysis):
    os.makedirs("reports", exist_ok=True)

    filename = f"reports/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    with open(filename, "w") as f:
        f.write("=== QAGENT REPORT ===\n\n")
        f.write(f"Command: {user_input}\n\n")
        f.write(f"Status: {analysis['status']}\n\n")
        f.write("Details:\n")
        f.write(analysis["details"])

    print(f"\nReport generated: {filename}")
