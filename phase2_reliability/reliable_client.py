import json
import sys
import os

# This lets Python find schemas.py in the same folder
sys.path.append(os.path.dirname(__file__))

import ollama
from pydantic import ValidationError
from rich.console import Console
from rich.panel import Panel
from schemas import AIResponse

console = Console()

# CORE FUNCTION — Ask with retry

def ask_with_retry(prompt: str, model: str = "llama3.2:3b", max_retries: int = 3):
    """
    Sends prompt to model and validates response against schema.
    Retries automatically up to max_retries times if response is invalid.
    """

    # Tell the model EXACTLY what JSON format to return
    system_prompt = """You are a helpful assistant.
You MUST respond ONLY in valid JSON format exactly like this:
{
  "answer": "your main answer here",
  "confidence": "high or medium or low",
  "key_points": ["point 1", "point 2", "point 3"],
  "word_count": 42
}
No extra text. No markdown. No explanation outside the JSON."""

    for attempt in range(1, max_retries + 1):
        console.print(f"\n[bold cyan]Attempt {attempt}/{max_retries}[/bold cyan]")

        try:
            # Call the model 
            response = ollama.chat(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": prompt}
                ]
            )

            raw_text = response["message"]["content"].strip()
            console.print(f"[dim]Raw output: {raw_text[:120]}[/dim]")

            # Clean up if model adds markdown fences 
            # Sometimes model returns ```json ... ``` we strip that
            if "```" in raw_text:
                raw_text = raw_text.split("```")[1]
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:]
                raw_text = raw_text.strip()

            # Step 1: Parse JSON
            parsed_json = json.loads(raw_text)
            console.print("[green]✓ JSON parsed successfully[/green]")

            # Step 2: Validate against Pydantic schema
            validated = AIResponse(**parsed_json)
            console.print("[green]✓ Schema validation passed[/green]")

            return validated  # Success — return the validated response

        except json.JSONDecodeError as e:
            # Model returned something that isn't valid JSON
            console.print(f"[red]✗ JSON error: {e}[/red]")
            console.print("[yellow]Retrying...[/yellow]")

        except ValidationError as e:
            # JSON was valid but missing required fields
            console.print(f"[red]✗ Schema error: {e}[/red]")
            console.print("[yellow]Retrying...[/yellow]")

        except Exception as e:
            console.print(f"[red]✗ Unexpected error: {e}[/red]")
            console.print("[yellow]Retrying...[/yellow]")

    # All retries exhausted
    console.print("\n[bold red]All retries failed.[/bold red]")
    return None


# DISPLAY FINAL RESULT 

def display_result(result: AIResponse):
    console.print("\n")
    console.print(Panel.fit(
        f"[bold]Answer:[/bold] {result.answer}\n\n"
        f"[bold]Confidence:[/bold] {result.confidence}\n\n"
        f"[bold]Key Points:[/bold]\n"
        + "\n".join(f"  • {pt}" for pt in result.key_points) +
        f"\n\n[bold]Word Count:[/bold] {result.word_count}",
        title="[bold green]✅ Validated AI Response[/bold green]",
        border_style="green"
    ))



# MAIN

if __name__ == "__main__":
    console.print("\n[bold green]Phase 2 — Reliability & Schema Validation[/bold green]")
    console.print("[dim]Testing that AI always returns structured JSON output[/dim]\n")

    # Test questions
    questions = [
        "What is machine learning?",
        "What is the difference between RAM and storage?",
    ]

    for question in questions:
        console.print(f"\n[bold yellow]Question:[/bold yellow] {question}")
        console.print("─" * 50)

        result = ask_with_retry(question)

        if result:
            display_result(result)
        else:
            console.print("[red]Failed to get valid response after all retries.[/red]")

    console.print("\n[bold green]Phase 2 Complete![/bold green]")