"""Demo script showcasing the multi-agent system"""
import logging
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.orchestrator import Orchestrator
from src.config import settings

console = Console()


def demo_metacognition():
    """Demonstrate metacognitive capabilities"""
    console.print(Panel.fit(
        "[bold cyan]Metacognitive Multi-Agent System Demo[/bold cyan]\n"
        "[dim]Showcasing self-aware, learning agents[/dim]",
        border_style="cyan"
    ))
    
    # Initialize
    console.print("\n[yellow]Initializing agents...[/yellow]")
    orchestrator = Orchestrator()
    
    # Show initial agent states
    console.print("\n[bold]Initial Agent States:[/bold]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Agent", style="cyan")
    table.add_column("State", style="green")
    table.add_column("Strengths", style="yellow")
    
    for agent in orchestrator.agents:
        status = agent.get_status()
        strengths = ", ".join(agent.self_model.get("strengths", []))
        table.add_row(agent.name, status["state"], strengths)
    
    console.print(table)
    
    # Run pipeline with progress
    console.print("\n[bold]Running Intelligence Pipeline:[/bold]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Processing...", total=None)
        result = orchestrator.run_pipeline()
        progress.update(task, completed=True)
    
    # Show results
    if result["success"]:
        console.print("\n[bold green]✅ Pipeline Completed Successfully![/bold green]")
        
        results_table = Table(show_header=True, header_style="bold blue")
        results_table.add_column("Metric", style="cyan")
        results_table.add_column("Value", style="green", justify="right")
        
        results_table.add_row("Titles Collected", str(result["collected_count"]))
        results_table.add_row("Titles Analyzed", str(result["analyzed_count"]))
        results_table.add_row("Articles Retrieved", str(result["retrieved_count"]))
        results_table.add_row("Execution Time", f"{result['execution_time']:.2f}s")
        
        console.print(results_table)
    
    # Show agent learning
    console.print("\n[bold]Agent Learning & Adaptation:[/bold]")
    
    for agent in orchestrator.agents:
        status = agent.get_status()
        console.print(f"\n[cyan]{agent.name}:[/cyan]")
        console.print(f"  • Thoughts generated: {status['thoughts_count']}")
        console.print(f"  • Actions taken: {status['actions_count']}")
        console.print(f"  • Reflections: {status['reflections_count']}")
        console.print(f"  • Success rate: {status['success_rate']:.1%}")
        
        if agent.self_model.get("learned_patterns"):
            console.print(f"  • Learned patterns: {len(agent.self_model['learned_patterns'])}")
    
    # Show system report
    console.print("\n" + "="*60)
    console.print(orchestrator.get_system_report())


def demo_memory_system():
    """Demonstrate memory system"""
    console.print("\n[bold cyan]Memory System Demo[/bold cyan]")
    
    orchestrator = Orchestrator()
    
    # Show memory statistics
    console.print("\n[yellow]Querying agent memories...[/yellow]")
    
    for agent in orchestrator.agents:
        memories = agent.memory.query(limit=5)
        console.print(f"\n[cyan]{agent.name} - Recent Memories:[/cyan]")
        
        for i, mem in enumerate(memories, 1):
            console.print(f"  {i}. Type: {mem.type.value}, Importance: {mem.importance:.2f}")


def demo_self_reference():
    """Demonstrate self-referential capabilities"""
    console.print("\n[bold cyan]Self-Reference Demo[/bold cyan]")
    
    orchestrator = Orchestrator()
    
    console.print("\n[yellow]Agent Self-Models:[/yellow]")
    
    for agent in orchestrator.agents:
        console.print(f"\n[cyan]{agent.name}:[/cyan]")
        console.print(f"  ID: {agent.id}")
        console.print(f"  Strengths: {agent.self_model.get('strengths', [])}")
        console.print(f"  Weaknesses: {agent.self_model.get('weaknesses', [])}")
        console.print(f"  Performance: Success={agent.success_count}, Fail={agent.failure_count}")


if __name__ == "__main__":
    # Set logging level
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Run demos
        demo_metacognition()
        demo_memory_system()
        demo_self_reference()
        
        console.print("\n[bold green]✨ Demo completed![/bold green]")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[bold red]Error: {e}[/bold red]")
