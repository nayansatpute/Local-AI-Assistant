import time
import json
import os
import ollama
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


# RUN BENCHMARK FOR ONE MODEL

def benchmark_single(model_name: str, prompt: str, runs: int = 3):
    results = []
    console.print(f"\n[bold cyan]Testing: {model_name}[/bold cyan]")

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
            "run"             : i + 1,
            "ttft"            : ttft,
            "total_time"      : total_time,
            "tps"             : tps,
            "token_count"     : token_count,
            "response_preview": full_response[:200]
        })
        console.print(
            f"[green]Done[/green] | "
            f"TTFT: [cyan]{ttft}s[/cyan] | "
            f"Speed: [green]{tps} tok/s[/green] | "
            f"Total: [blue]{total_time}s[/blue]"
        )

    return results


# RUN ALL MODELS

def run_comparison(models: list, prompt: str, runs: int = 3):
    all_results = {}
    for model in models:
        all_results[model] = benchmark_single(model, prompt, runs)
    return all_results



# CALCULATE SUMMARY FOR ONE MODEL

def summarize(model_name: str, results: list):
    avg_ttft  = round(sum(r["ttft"]       for r in results) / len(results), 3)
    avg_tps   = round(sum(r["tps"]        for r in results) / len(results), 1)
    avg_total = round(sum(r["total_time"] for r in results) / len(results), 2)
    avg_tokens= round(sum(r["token_count"]for r in results) / len(results), 1)

    return {
        "model"      : model_name,
        "avg_ttft"   : avg_ttft,
        "avg_tps"    : avg_tps,
        "avg_total"  : avg_total,
        "avg_tokens" : avg_tokens
    }



# DISPLAY COMPARISON TABLE

def display_comparison(all_results: dict):
    summaries = [summarize(m, r) for m, r in all_results.items()]

    # Find winners in each category
    fastest_tps   = max(summaries, key=lambda x: x["avg_tps"])
    lowest_ttft   = min(summaries, key=lambda x: x["avg_ttft"])
    most_tokens   = max(summaries, key=lambda x: x["avg_tokens"])

    # ── Main comparison table ──
    table = Table(
        title="Model Comparison Report",
        header_style="bold magenta",
        show_lines=True
    )
    table.add_column("Model",        style="cyan",   width=20)
    table.add_column("Avg TTFT(s)",  style="yellow", width=12)
    table.add_column("Avg tok/s",    style="green",  width=12)
    table.add_column("Avg Total(s)", style="blue",   width=13)
    table.add_column("Avg Tokens",   style="white",  width=12)
    table.add_column("Badges",       style="bold",   width=18)

    for s in summaries:
        badges = []
        if s["model"] == fastest_tps["model"]:
            badges.append("Fastest")
        if s["model"] == lowest_ttft["model"]:
            badges.append("Low TTFT")
        if s["model"] == most_tokens["model"]:
            badges.append("Verbose")

        table.add_row(
            s["model"],
            str(s["avg_ttft"]),
            str(s["avg_tps"]),
            str(s["avg_total"]),
            str(s["avg_tokens"]),
            " ".join(badges) if badges else "—"
        )

    console.print("\n")
    console.print(table)

    # Winner panel
    console.print(Panel.fit(
        f"[bold]Fastest Model:[/bold]    {fastest_tps['model']} "
        f"({fastest_tps['avg_tps']} tok/s)\n"
        f"[bold]Lowest Latency:[/bold]   {lowest_ttft['model']} "
        f"({lowest_ttft['avg_ttft']}s TTFT)\n"
        f"[bold]Most Detailed:[/bold]    {most_tokens['model']} "
        f"({most_tokens['avg_tokens']} tokens avg)\n\n"
        f"[dim] Smaller models are faster but may give shorter answers.\n"
        f"   Larger models are slower but give more detailed responses.[/dim]",
        title="[bold green] Comparison Summary[/bold green]",
        border_style="green"
    ))

    return summaries



# SAVE FULL REPORT TO JSON

def save_report(all_results: dict, summaries: list):
    os.makedirs("phase3_comparison/results", exist_ok=True)

    report = {
        "test_prompt" : TEST_PROMPT,
        "models_tested": list(all_results.keys()),
        "summaries"   : summaries,
        "raw_results" : {
            model: results
            for model, results in all_results.items()
        }
    }

    path = "phase3_comparison/results/comparison_report.json"
    with open(path, "w") as f:
        json.dump(report, f, indent=2)

    console.print(f"\n[dim]Full report saved → {path}[/dim]")



# MAIN

TEST_PROMPT = "Explain what a neural network is in 3 sentences."

if __name__ == "__main__":
    MODELS = [
        "llama3.2:1b",
        "llama3.2:3b",
    ]

    console.print("\n[bold green]Phase 3 — Model Comparison[/bold green]")
    console.print("[dim]Close all other apps for clean results[/dim]\n")
    console.print(f"[yellow]Comparing: {' vs '.join(MODELS)}[/yellow]")
    console.print(f"[yellow]Prompt: {TEST_PROMPT}[/yellow]\n")

    # Run all benchmarks
    all_results = run_comparison(MODELS, TEST_PROMPT, runs=3)

    # Display and save
    summaries = display_comparison(all_results)
    save_report(all_results, summaries)

    console.print("\n[bold green] Phase 3 Complete![/bold green]")
    console.print("[dim]Check phase3_comparison/results/comparison_report.json[/dim]")