"""Main entry point for the multi-agent system"""
import logging
from rich.logging import RichHandler
from rich.console import Console

from .orchestrator import Orchestrator
from .config import settings

# Setup logging
logging.basicConfig(
    level=settings.log_level,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)]
)

logger = logging.getLogger(__name__)
console = Console()


def main():
    """Main execution function"""
    console.print("[bold cyan]Multi-Agent News Intelligence System[/bold cyan]")
    console.print("[dim]Version 1.0.0 - Metacognitive Agentic Architecture[/dim]\n")
    
    # Initialize orchestrator
    orchestrator = Orchestrator()
    
    # Run pipeline
    result = orchestrator.run_pipeline()
    
    # Display results
    if result["success"]:
        console.print("\n[bold green]✅ Pipeline completed successfully![/bold green]\n")
        console.print(f"📊 Collected: {result['collected_count']} titles")
        console.print(f"🔍 Analyzed: {result['analyzed_count']} titles")
        console.print(f"📥 Retrieved: {result['retrieved_count']} articles")
        if result.get('generated_count', 0) > 0:
            console.print(f"✍️  Generated: {result['generated_count']} articles")
        console.print(f"⏱️  Time: {result['execution_time']:.2f}s\n")
    else:
        console.print("\n[bold red]❌ Pipeline failed[/bold red]")
        console.print(f"Error: {result.get('error')}\n")
    
    # Display system report
    console.print("\n" + orchestrator.get_system_report())


if __name__ == "__main__":
    main()
