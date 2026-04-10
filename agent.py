# agent.py

import sys
from core.agent import Agent

def main():
    if len(sys.argv) < 2:
        print("Usage: python agent.py \"your command\"")
        return

    user_input = sys.argv[1]

    agent = Agent()
    agent.run(user_input)


if __name__ == "__main__":
    main()