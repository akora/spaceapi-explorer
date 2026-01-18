#!/usr/bin/env python3
"""
Example: Create an interactive world map of hackerspaces.
This script fetches space data and generates an HTML map with all locations.
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add the parent directory to the path so we can import spaceapi
sys.path.insert(0, str(Path(__file__).parent.parent))

from spaceapi import SpaceAPIClient
from spaceapi.analyzer import SpaceAnalyzer
from spaceapi.visualizer import SpaceVisualizer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel

console = Console()


def main():
    """Create an interactive world map of hackerspaces."""
    
    console.print(Panel.fit("Hackerspace World Map Generator", style="bold blue"))
    
    # Initialize client and fetch data
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        
        # Step 1: Fetch directory
        task1 = progress.add_task("Fetching SpaceAPI directory...", total=None)
        try:
            client = SpaceAPIClient()
            directory = client.get_directory()
            progress.update(task1, description=f"Directory fetched: {len(directory.spaces)} spaces")
            
        except Exception as e:
            console.print(f"[red]Error fetching directory: {e}[/red]")
            return
        
        # Step 2: Fetch space statuses (limit to first 50 for demo)
        task2 = progress.add_task("Fetching space statuses...", total=50)
        space_urls = list(directory.spaces.values())[:50]  # Limit for demo
        
        spaces_data = []
        for i, url in enumerate(space_urls):
            space_status = client.get_space_status(str(url))
            if space_status:
                spaces_data.append(space_status)
            progress.update(task2, advance=1, description=f"Fetched {i+1}/{len(space_urls)} spaces")
        
        progress.update(task2, description=f"Successfully fetched {len(spaces_data)} space statuses")
    
    console.print(f"\n[green]Successfully fetched data for {len(spaces_data)} hackerspaces![/green]")
    
    # Analyze the data
    analyzer = SpaceAnalyzer()
    analyzer.load_spaces(spaces_data)
    
    # Get basic statistics
    stats = analyzer.get_basic_stats()
    console.print("\n[bold]Data Summary:[/bold]")
    console.print(f"• Total spaces: {stats['total_spaces']}")
    console.print(f"• Spaces with location: {stats['spaces_with_location']}")
    console.print(f"• Spaces with status: {stats['spaces_with_state']}")
    console.print(f"• Currently open: {stats['currently_open']}")
    
    # Create visualizations
    visualizer = SpaceVisualizer()
    
    # Generate world map
    console.print("\n[bold]Generating visualizations...[/bold]")
    
    # 1. Interactive world map
    console.print("• Creating interactive world map...")
    world_map = visualizer.create_world_map(spaces_data)
    map_filename = f"hackerspaces_world_map_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    world_map.save(map_filename)
    console.print(f"  [green]✓[/green] Saved as {map_filename}")
    
    # 2. Geographic distribution plot
    console.print("• Creating geographic distribution plot...")
    geo_plot_filename = f"geographic_distribution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    visualizer.plot_geographic_distribution(spaces_data, save_path=geo_plot_filename)
    console.print(f"  [green]✓[/green] Saved as {geo_plot_filename}")
    
    # 3. Opening status pie chart
    console.print("• Creating opening status chart...")
    status_plot_filename = f"opening_status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    visualizer.plot_opening_status_pie(spaces_data, save_path=status_plot_filename)
    console.print(f"  [green]✓[/green] Saved as {status_plot_filename}")
    
    # 4. Contact methods chart
    console.print("• Creating contact methods chart...")
    contact_plot_filename = f"contact_methods_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    visualizer.plot_contact_methods(spaces_data, save_path=contact_plot_filename)
    console.print(f"  [green]✓[/green] Saved as {contact_plot_filename}")
    
    console.print(Panel.fit(
        f"All visualizations generated successfully!\n\n"
        f"Open {map_filename} in your browser to see the interactive map.",
        style="bold green"
    ))


if __name__ == "__main__":
    main()
