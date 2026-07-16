"""Terminal chat loop - run with: python run_cli.py"""
from app.config import DEFAULT_RESUME_PATH
from app.graph.builder import run_agent

if __name__ == "__main__":
    print("=" * 60)
    print("LangGraph AI Agent")
    print("Type 'exit' to quit")
    print("=" * 60)

    while True:
        question = input("\nYou : ")

        if question.lower() == "exit":
            print("\nGoodbye!")
            break

        result = run_agent(question, str(DEFAULT_RESUME_PATH))
        print("\nBot :")
        print(result["answer"])