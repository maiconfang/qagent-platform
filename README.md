# 🤖 QAgent Platform — Agentic QA Engine

An intelligent QA automation orchestrator that executes tests, analyzes results, and makes decisions based on real evidence.

---

## 💡 Overview

QAgent Platform is an **Agentic QA Engine** designed to simulate how a real QA engineer thinks:

- Execute tests
- Analyze failures
- Classify issues
- Decide next actions
- Generate reports

All of this **automatically, consistently, and based on evidence — not assumptions**.

---

## 🧠 Core Concept

Traditional automation:
> Run tests → Get results

QAgent Platform:
> Run tests → Understand results → Decide what to do next

---

## ⚙️ Architecture

Agent  
  ↓  
Executor (Playwright CLI)  
  ↓  
Analyzer (Failure classification)  
  ↓  
Decision Engine (CONTINUE / RETRY / STOP)  
  ↓  
Reporter (JSON + Insights)  

---

## 🔍 Features

✔ Playwright test execution (UI + API)  
✔ Failure classification (TIMEOUT, LOCATOR, API, etc.)  
✔ Adaptive decision engine  
✔ Multi-phase execution strategy  
✔ Flaky detection (phase-level and test-level)  
✔ Persistent execution state  
✔ Structured JSON reports  
✔ Designed for multi-project scalability  

---

## 🧪 Execution Flow

Example command:

```bash
python agent.py "validate provinces" --project taskmanagerplus
```

### What happens:

1. Detect domain → `provinces`
2. Load project configuration
3. Execute phases:

- HIGH_IMPACT
- EXTENDED
- FULL (optional)

4. Analyze results
5. Decide next step:

- CONTINUE
- RETRY
- STOP

---

## 📊 Example Output

```
[AGENT][HIGH_IMPACT | RESULT] Status: SUCCESS
[AGENT][DECISION] Decision: CONTINUE

[AGENT][EXTENDED | RESULT] Status: SUCCESS
[AGENT][DECISION] Decision: DONE
```

---

## 🧾 Example Final Report

```
Change detected: New field added to Provinces page

Execution summary:
- UI tests executed (Playwright)
- API validations performed
- Jenkins pipeline triggered
- AI Analyzer used for failure classification

Results:
- 15 tests executed
- 0 failures
- 2 new validation tests generated

Confidence level: HIGH

Conclusion:
No issues detected. The system remains stable after the change.
```

---

## 🧠 Intelligence Layer

The Analyzer applies **deterministic logic + heuristics**, such as:

- Timeout → UI_TIMEOUT
- 404 → RESOURCE_NOT_FOUND
- 403 → AUTH_FAILURE
- Invalid input → VALIDATION_ERROR

No hallucination.  
Only **evidence-based classification**.

---

## 🔁 Decision Engine

The system decides dynamically:

| Condition | Action |
|----------|--------|
| Critical failure | STOP |
| Minor issues | RETRY |
| Stable execution | CONTINUE |

---

## 📂 Project Structure

```
qagent-platform/
├── agent.py
├── analyzer/
├── executor/
├── decision_engine/
├── reporter/
├── configs/
└── reports/
```

---

## 🔧 Configuration

Example `.env`:

```
TEST_PROJECT_PATH=C:\dev\workspace\taskmanagerplus-tests\ui-tests
PLAYWRIGHT_COMMAND=npx.cmd playwright test
MAX_ATTEMPTS=2
```

---
## ⚙️ Runtime Context & Integration

### 📂 External Test Project

This system integrates with an external Playwright test project:


../taskmanagerplus-tests/ui-tests


The agent reads structured test results from:


../taskmanagerplus-tests/ui-tests/reports/ui/playwright-report.json


### 🧠 Data Source Strategy

- Playwright JSON report is the **primary source of truth**
- Stdout parsing is used only as a **fallback mechanism**
- This ensures:
  - structured and reliable data
  - improved test analysis accuracy
  - better scalability for CI/CD environments

### 🧪 Current Capabilities

The system currently supports:

- Flaky detection (phase-level and test-level)
- Stability score calculation per test (%)
- Decision engine (CONTINUE / RETRY / STOP)
- Persistent execution state
- HTML reporting with insights and stability metrics

### 🏗️ Architecture Principles

- Multi-project integration (test project + agent system)
- Evidence-based analysis (no assumptions)
- Incremental evolution (no breaking changes)
- Production-oriented design
---

## 📈 Roadmap

- [ ] HTML Report (visual insights)
- [ ] AI-powered root cause analysis
- [ ] Integration with AI Analyzer project
- [ ] Multi-project orchestration
- [ ] CI/CD deep integration

---

## 🎯 Vision

Move from:

> “Running tests”

To:

> “Understanding quality automatically”

---

## 👨‍💻 Author

**Maicon Fang**  
QA Engineer | Test Automation | Agentic QA  

📌 Portfolio: https://maiconfang.github.io/portfolio/  
📌 YouTube: [Maicon Fang IT and Quality Assurance](https://www.youtube.com/@maiconfangitqa)

---

## ⭐ Final Thought

This project is not just about automation.

It’s about building a system that **thinks like QA**.
