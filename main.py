from app.runtime import JarvisRuntime


def main():
    runtime = JarvisRuntime()

    print("JARVIS started. Type 'exit' to quit.")

    while True:
        user_input = input("You: ").strip()

        if any(
            word in user_input.lower()
            for word in ["exit", "quit", "bye", "goodbye"]
        ):
            print("JARVIS: Goodbye 👋")
            break

        response = runtime.run(user_input)

        plan = response["plan"]
        results = response["results"]
        context = response["context"]

        if plan is None or not plan.steps:
            print("⚠️ No valid plan generated.")
            continue

        print("PLAN:", plan)

        for result in results:
            print("RESULT:", result)

        if context:
            print("\n🧠 CONTEXT STATE:")
            print("History:", context.history)
            print("🧠 CONTEXT:", context.debug())


if __name__ == "__main__":
    main()