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

        </div>
    </body>
    </html>
    """

    with open("reports/report.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("[REPORT] HTML report generated at reports/report.html")