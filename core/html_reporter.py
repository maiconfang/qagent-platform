def humanize_error(error_type):
    mapping = {
        "UI_TIMEOUT": "UI Timeout",
        "ASSERTION_TIMEOUT": "Assertion Timeout",
        "LOCATOR_FAILURE": "Locator Failure",
        "ASSERTION_FAILURE": "Assertion Failure"
    }

    return mapping.get(error_type, error_type.replace("_", " ").title())


def get_root_cause_hint(error_type, error_message):
    error_message = (error_message or "").lower()

    if error_type == "UI_TIMEOUT":
        if "locator" in error_message:
            return "Element not found → locator may be incorrect or page not ready"

        if "timeout" in error_message:
            return "Test exceeded timeout → possible infinite wait or missing element"

        if "navigation" in error_message:
            return "Page navigation issue → possible redirect or slow load"

        return "Timeout in UI interaction → possible slow rendering or sync issue"

    if error_type == "ASSERTION_TIMEOUT":
        if "tohavetext" in error_message or "not found" in error_message:
            return "Assertion failed → element not found or content not loaded"
        return "Assertion timeout → expected condition not met in time"

    if error_type == "ASSERTION_FAILURE":
        return "Assertion mismatch → actual value differs from expected"

    return "Unknown issue → requires deeper investigation"


def generate_html_report(report_data):
    status = report_data.get("finalStatus", "UNKNOWN")

    decision = report_data.get("decision")

    if isinstance(decision, dict):
        decision_display = decision.get("action", "UNKNOWN")
    else:
        decision_display = decision or "UNKNOWN"

    status_class = "success"
    if status == "FAILURE":
        status_class = "fail"

    # Detect flaky
    is_flaky = any("FLAKY DETECTED" in i for i in report_data.get("insights", []))

    # NEW: separate flaky badge
    flaky_badge = ""
    if is_flaky:
        flaky_badge = '<span class="badge flaky">FLAKY</span>'

    # History (from insights or decision)
    history_display = ""
    for insight in report_data.get("insights", []):
        if "history=" in insight:
            history_display = insight.split("history=")[-1].replace(")", "")
            break

    # 🔥 NEW: extract stability insights
    stability_items = [
        i for i in report_data.get("insights", [])
        if i.startswith("STABILITY:")
    ]

    filtered_insights = [
        i for i in report_data.get("insights", [])
        if not i.startswith("STABILITY:")
    ]

    insights_html = "".join(f"<li>{i}</li>" for i in filtered_insights)

    stability_html = ""

    for item in stability_items:
        # Example: STABILITY: test → 43% stable
        try:

            parts = item.split("→")
            if len(parts) != 2:
                continue

            name_part, value_part = parts

            test_name = name_part.replace("STABILITY:", "").strip()
            stability_value = value_part.replace("stable", "").strip()

            value_num = int(stability_value.replace("%", ""))

            # Color logic
            if value_num >= 85:
                color = "success"
            elif value_num >= 60:
                color = "flaky"
            else:
                color = "fail"

            stability_html += f"""
            <li>
                {test_name} →
                <span class="badge {color}">
                    {value_num}%
                </span>
            </li>
            """

        except Exception:
            continue

    # 🔥 NEW: Failed tests details (enhanced UI)

    failed_tests_html = ""
    rank = 1
   
    # 👉 SAME mapping used in agent.py (KEEP CONSISTENT)
    error_priority_map = {
        "UI_TIMEOUT": "HIGH",
        "ASSERTION_TIMEOUT": "MEDIUM",
        "ASSERTION_FAILURE": "MEDIUM",
        "UNKNOWN": "LOW"
    }

    for test in report_data.get("tests", []):
        if test.get("status") not in ["failed", "timedOut"]:
            continue

        error_type = test.get("error_type") or "UNKNOWN"
        priority = error_priority_map.get(error_type, "LOW")
        duration = test.get("duration", 0)

        # 🎨 CSS class
        priority_class = {
            "HIGH": "priority-high",
            "MEDIUM": "priority-medium",
            "LOW": "priority-low"
        }.get(priority, "priority-low")

        # 🔥 Icons
        priority_icon = {
            "HIGH": "🔥",
            "MEDIUM": "⚠️",
            "LOW": "ℹ️"
        }.get(priority, "ℹ️")

        # 🏆 Ranking icon
        rank_icon = {
            1: "🥇",
            2: "🥈",
            3: "🥉"
        }.get(rank, f"#{rank}")

        root_cause_hint = get_root_cause_hint(error_type, test.get("error"))

        failed_tests_html += f"""
        <li class="test-card {priority_class}">
            <div class="test-header">
                <strong>{rank_icon} {priority_icon} {test.get("name")}</strong>
            </div>

            <div class="test-meta">
                <span class="badge {priority_class}">
                    {priority}
                </span>

                <span class="badge fail">
                    {humanize_error(error_type)}
                </span>

                <span class="duration">
                    ⏱️ {duration} ms
                </span>
            </div>

            <div class="test-error">
                {test.get("error", "No error message")}
            </div>

            <div class="test-hint">
                💡 <strong>Possible Root Cause:</strong> {root_cause_hint}
            </div>

            
        </li>
        """
        rank += 1
        
    html = f"""
    <html>
    <head>
        <title>QAgent Report</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #0f172a;
                color: #e2e8f0;
                padding: 20px;
            }}

            .container {{
                max-width: 900px;
                margin: auto;
            }}

            .card {{
                background-color: #1e293b;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                box-shadow: 0 0 10px rgba(0,0,0,0.3);
            }}

            .success {{ color: #22c55e; }}
            .fail {{ color: #ef4444; }}
            .flaky {{ color: #f59e0b; }}

            .badge {{
                padding: 5px 10px;
                border-radius: 5px;
                font-weight: bold;
            }}

            .badge.success {{ background: #22c55e; color: black; }}
            .badge.fail {{ background: #ef4444; color: white; }}
            .badge.flaky {{ background: #f59e0b; color: black; }}

            h1, h2 {{
                margin-bottom: 10px;
            }}

            ul {{
                padding-left: 20px;
            }}

            .history {{
                font-family: monospace;
                background: #020617;
                padding: 10px;
                border-radius: 5px;
                margin-top: 10px;
            }}


            /* ===== Test Cards ===== */
            .test-card {{
                border: 1px solid #334155;
                border-radius: 10px;
                padding: 12px;
                margin-bottom: 10px;
                background-color: #020617;
                transition: transform 0.1s ease;
            }}

            .test-card:hover {{
                transform: scale(1.01);
            }}

            /* Header */
            .test-header {{
                font-size: 14px;
                margin-bottom: 6px;
            }}

            /* Meta */
            .test-meta {{
                margin-bottom: 6px;
            }}

            .duration {{
                margin-left: 10px;
                font-size: 12px;
                color: #94a3b8;
            }}

            /* Error */
            .test-error {{
                font-size: 12px;
                color: #cbd5f5;
            }}

            .test-hint {{
                margin-top: 8px;
                font-size: 12px;
                color: #93c5fd;
                background-color: rgba(59, 130, 246, 0.1);
                padding: 6px;
                border-radius: 6px;
            }}

            /* Priority border */
            .priority-high {{
                border-left: 5px solid #ef4444;
            }}

            .priority-medium {{
                border-left: 5px solid #f59e0b;
            }}

            .priority-low {{
                border-left: 5px solid #22c55e;
            }}

            /* Priority badges */
            .badge.priority-high {{
                background: #ef4444;
                color: white;
            }}

            .badge.priority-medium {{
                background: #f59e0b;
                color: black;
            }}

            .badge.priority-low {{
                background: #22c55e;
                color: black;
            }}

        </style>
    </head>

    <body>
        <div class="container">

            <div class="card">
                <h1>🚀 QAgent Report</h1>

                <h2>Status:
                    <span class="badge {status_class}">
                        {status}
                    </span>
                    {flaky_badge}
                </h2>

                <p><strong>Command:</strong> {report_data.get("command")}</p>
                <p><strong>Duration:</strong> {report_data.get("duration")}s</p>
            </div>

            <div class="card">
                <h2>📊 Phase Details</h2>

                <p><strong>Phase:</strong> {report_data.get("phase")}</p>
                <p><strong>Decision:</strong> {decision_display}</p>

                <div class="history">
                    <strong>History:</strong><br>
                    {history_display if history_display else "No history available"}
                </div>
            </div>

            
            <div class="card">
                <h2>📊 Stability</h2>
                <ul>
                    {stability_html if stability_html else "<li>No stability data</li>"}
                </ul>
            </div>

            <div class="card">
                <h2>🧠 Insights</h2>
                <ul>
                    {insights_html}
                </ul>
            </div>

            <div class="card">
                <h2>❌ Failed Tests Details</h2>
                <ul>
                    {failed_tests_html if failed_tests_html else "<li>No failed tests</li>"}
                </ul>
            </div>

        </div>
    </body>
    </html>
    """

    with open("reports/report.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("[REPORT] HTML report generated at reports/report.html")