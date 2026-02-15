"""Setup script for LLM model"""
import os
from pathlib import Path
import requests
from rich.console import Console
from rich.progress import Progress, DownloadColumn, BarColumn, TextColumn

console = Console()


def download_model():
    """Download Mistral-7B model"""
    console.print("[bold cyan]LLM Model Setup[/bold cyan]\n")
    
    model_dir = Path("models")
    model_dir.mkdir(exist_ok=True)
    
    model_path = model_dir / "mistral-7b-v0.3-sarcasm-scrolls-4k-q4_k_m.gguf"
    
    if model_path.exists():
        console.print(f"✅ Model already exists at {model_path}")
        return
    
    console.print("[yellow]Model not found. You have two options:[/yellow]\n")
    console.print("1. Download automatically (requires ~4GB)")
    console.print("2. Place your own model manually\n")
    
    choice = input("Choose option (1/2) or 'skip' to continue without LLM: ").strip()
    
    if choice == "1":
        # Example URL - replace with actual model URL
        url = "https://huggingface.co/TheBloke/Mistral-7B-v0.3-GGUF/resolve/main/mistral-7b-v0.3.Q4_K_M.gguf"
        
        console.print(f"\n[yellow]Downloading model...[/yellow]")
        console.print("[dim]This may take a while (4GB file)[/dim]\n")
        
        try:
            response = requests.get(url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            
            with Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                DownloadColumn(),
                console=console
            ) as progress:
                task = progress.add_task("Downloading...", total=total_size)
                
                with open(model_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        progress.update(task, advance=len(chunk))
            
            console.print(f"\n✅ Model downloaded to {model_path}")
            
        except Exception as e:
            console.print(f"\n[red]❌ Download failed: {e}[/red]")
            console.print("\n[yellow]Please download manually:[/yellow]")
            console.print(f"1. Download from: {url}")
            console.print(f"2. Place in: {model_path}")
    
    elif choice == "2":
        console.print(f"\n[yellow]Please place your GGUF model at:[/yellow]")
        console.print(f"  {model_path}")
        console.print("\n[dim]Supported formats: .gguf (llama.cpp compatible)[/dim]")
    
    else:
        console.print("\n[yellow]⏭️  Skipping LLM setup[/yellow]")
        console.print("[dim]The system will work without article generation[/dim]")
        
        # Disable LLM in config
        env_path = Path(".env")
        if env_path.exists():
            with open(env_path, 'a') as f:
                f.write("\nLLM_ENABLED=false\n")


def install_llm_dependencies():
    """Install llama-cpp-python"""
    console.print("\n[bold cyan]Installing LLM Dependencies[/bold cyan]\n")
    
    try:
        import llama_cpp
        console.print("✅ llama-cpp-python already installed")
    except ImportError:
        console.print("[yellow]Installing llama-cpp-python...[/yellow]")
        console.print("[dim]This may take a few minutes[/dim]\n")
        
        import subprocess
        try:
            subprocess.check_call([
                "pip", "install", "llama-cpp-python"
            ])
            console.print("\n✅ llama-cpp-python installed successfully")
        except Exception as e:
            console.print(f"\n[red]❌ Installation failed: {e}[/red]")
            console.print("\n[yellow]Please install manually:[/yellow]")
            console.print("  pip install llama-cpp-python")


if __name__ == "__main__":
    console.print("\n[bold]Multi-Agent System - LLM Setup[/bold]\n")
    
    install_llm_dependencies()
    download_model()
    
    console.print("\n[bold green]✅ Setup complete![/bold green]")
    console.print("\n[dim]You can now run: python run.py[/dim]\n")
