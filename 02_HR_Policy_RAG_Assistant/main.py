from hr_assistant.pipeline import ask, build_hr_assistant

def main():
    print("Building the HR assistant...")
    agent = build_hr_assistant()
    print("HR assistant is ready. You can now ask questions.")

    demo_questions = [
        "What is the company's policy on remote work?",
        "How many vacation days do employees get per year?",
        "What is the procedure for reporting harassment?",
    ]

    for question in demo_questions:
        print(f"\nQuestion: {question}")
        answer = ask(agent, question)
        print(f"Answer: {answer}")


if __name__ == "__main__":
    main()