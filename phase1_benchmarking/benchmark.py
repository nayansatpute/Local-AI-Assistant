import time
import json
import os
import ollama
from rich.console import Console
from rich.table import Table

console = Console()

def benchmark_model(model_name: str, prompt: str, runs: int = 3):
    results = []
    console.print(f"\n[bold cyan]Benchmarking: {model_name}[/bold cyan]\n")

    for i in range(runs):
        console.print(f"  Run {i+1}/{runs} ... ", end="")

        start_time       = time.time()
        first_token_time = None
        full_response    = ""
        token_count      = 0

        stream = ollama.chat(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )

        for chunk in stream:
            content = chunk["message"]["content"]
            if first_token_time is None and content.strip():
                first_token_time = time.time()
            full_response += content
            token_count   += 1

        end_time   = time.time()
        ttft       = round(first_token_time - start_time, 3)
        total_time = round(end_time - start_time, 2)
        tps        = round(token_count / total_time, 1)

        results.append({
            "run": i+1, "ttft": ttft,
            "total_time": total_time, "tps": tps,
            "token_count": token_count
        })
        console.print(f"[green]Done[/green] | TTFT: {ttft}s | Speed: {tps} tok/s | Total: {total_time}s")

    return results

def display_results(model_name, results):
    table = Table(title=f"Results: {model_name}", header_style="bold magenta")
    table.add_column("Run",        style="dim")
    table.add_column("TTFT (s)",   style="cyan")
    table.add_column("Total (s)",  style="blue")
    table.add_column("Tokens/sec", style="green")

    for r in results:
        table.add_row(str(r["run"]), str(r["ttft"]),
                      str(r["total_time"]), str(r["tps"]))

    avg_ttft  = round(sum(r["ttft"] for r in results) / len(results), 3)
    avg_tps   = round(sum(r["tps"]  for r in results) / len(results), 1)
    avg_total = round(sum(r["total_time"] for r in results) / len(results), 2)

    table.add_section()
    table.add_row("[bold]AVG[/bold]",
                  f"[bold]{avg_ttft}[/bold]",
                  f"[bold]{avg_total}[/bold]",
                  f"[bold]{avg_tps}[/bold]")
    console.print(table)
    return {"model": model_name, "avg_ttft": avg_ttft, "avg_tps": avg_tps}

def save_results(model_name, results):
    os.makedirs("phase1_benchmarking/results", exist_ok=True)
    filename = f"phase1_benchmarking/results/{model_name.replace(':', '_')}.json"
    with open(filename, "w") as f:
        json.dump({"model": model_name, "runs": results}, f, indent=2)
    console.print(f"\n[dim]Saved → {filename}[/dim]")

if __name__ == "__main__":
    MODEL       = "llama3.2:3b"
    TEST_PROMPT = "Explain what a neural network is in 3 sentences."

    console.print("\n[bold green]Phase 1 — Benchmarking[/bold green]")
    results = benchmark_model(MODEL, TEST_PROMPT, runs=3)
    display_results(MODEL, results)
    save_results(MODEL, results)
    console.print("\n[bold green]Phase 1 Complete![/bold green]")