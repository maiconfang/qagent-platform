import sys
from core.runner import run_tests
from core.analyzer import analyze_results
from core.reporter import generate_report
from utils.logger import log

def main():
    if len(sys.argv) < 2:
        print("Usage: python agent.py 'your command'")
        return

    user_input = sys.argv[1]
    log(f"Received command: {user_input}")

    test_results = run_tests()
    analysis = analyze_results(test_results)
    generate_report(user_input, analysis)

if __name__ == "__main__":
    main()
