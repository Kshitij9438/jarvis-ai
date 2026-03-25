from rich.console import Console
from brain.llm import LLM

console = Console()

class CLI:
    def __init__(self):
        self.llm = LLM()

    def run(self):
        console.print("[bold green]JARVIS CLI started. Type 'exit' to quit.[/bold green]")

        while True:
            user_input = input("\nYou: ").strip()
            if not user_input:
                continue

            if user_input.lower() == "exit":
                break

            response = self.llm.generate(user_input)
            console.print(f"[bold cyan]JARVIS:[/bold cyan] {response}")

