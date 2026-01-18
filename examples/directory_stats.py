#!/usr/bin/env python3
"""
Example: Get basic statistics about the SpaceAPI directory.
This script fetches the directory and provides basic insights.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import spaceapi
sys.path.insert(0, str(Path(__file__).parent.parent))

from spaceapi import SpaceAPIClient
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

console = Console()


def main():
    """Fetch and display SpaceAPI directory statistics."""
    
    console.print(Panel.fit("SpaceAPI Directory Statistics", style="bold blue"))
    
    # Initialize client
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        task = progress.add_task("Fetching SpaceAPI directory...", total=None)
        
        try:
            client = SpaceAPIClient()
            directory = client.get_directory()
            progress.update(task, description="Directory fetched successfully!")
            
        except Exception as e:
            console.print(f"[red]Error fetching directory: {e}[/red]")
            return
    
    # Display basic stats
    console.print(f"\n[green]Found {len(directory.spaces)} hackerspaces in the directory![/green]")
    
    # Create a table with sample spaces
    table = Table(title="Sample Hackerspaces")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("URL", style="magenta")
    
    # Show first 20 spaces
    sample_spaces = list(directory.spaces.items())[:20]
    for name, url in sample_spaces:
        table.add_row(name, str(url))
    
    console.print(table)
    
    # Get directory stats
    stats = client.get_directory_stats()
    
    console.print("\n[bold]Directory Statistics:[/bold]")
    console.print(f"• Total spaces: {stats['total_spaces']}")
    console.print(f"• Last updated: {stats['last_updated']}")
    
    # Search functionality demo
    console.print("\n[bold]Search Examples:[/bold]")
    
    search_terms = ["hack", "lab", "space", "maker"]
    for term in search_terms:
        matching_urls = client.search_spaces(term)
        console.print(f"• Spaces containing '{term}': {len(matching_urls)}")
        if matching_urls:
            # Show first 3 matches
            for url in matching_urls[:3]:
                # Find the space name for this URL
                name = next((name for name, space_url in directory.spaces.items() 
                           if str(space_url) == url), "Unknown")
                console.print(f"  - {name}")
    
    console.print(f"\n[dim]... and {len(matching_urls) - 3} more[/dim]" if len(matching_urls) > 3 else "")
    
    console.print(Panel.fit("Directory statistics complete!", style="bold green"))


if __name__ == "__main__":
    main()
