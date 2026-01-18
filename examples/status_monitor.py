#!/usr/bin/env python3
"""
Example: Monitor real-time status of hackerspaces.
This script fetches current status information and displays it in a nice format.
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timezone

# Add the parent directory to the path so we can import spaceapi
sys.path.insert(0, str(Path(__file__).parent.parent))

from spaceapi import SpaceAPIClient
from spaceapi.analyzer import SpaceAnalyzer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.live import Live
from rich.layout import Layout
from rich.text import Text

console = Console()


def create_status_table(spaces_data):
    """Create a rich table showing space statuses."""
    table = Table(title="Hackerspace Status Monitor")
    table.add_column("Space Name", style="cyan", no_wrap=True)
    table.add_column("Status", style="bold")
    table.add_column("Location", style="dim")
    table.add_column("Last Change", style="dim")
    table.add_column("Message", style="italic")
    
    for space in spaces_data:
        # Status with color
        if space.state and space.state.open is True:
            status = "[green]OPEN[/green]"
        elif space.state and space.state.open is False:
            status = "[red]CLOSED[/red]"
        else:
            status = "[yellow]UNKNOWN[/yellow]"
        
        # Location info
        location = "N/A"
        if space.location and space.location.address:
            location = space.location.address
        elif space.location and space.location.lat and space.location.lon:
            location = f"{space.location.lat:.2f}, {space.location.lon:.2f}"
        
        # Last change time
        last_change = "N/A"
        if space.state and space.state.lastchange:
            timestamp = datetime.fromtimestamp(space.state.lastchange, tz=timezone.utc)
            last_change = timestamp.strftime("%H:%M UTC")
        
        # Status message
        message = space.state.message if space.state and space.state.message else ""
        
        table.add_row(
            space.space,
            status,
            location,
            last_change,
            message
        )
    
    return table


def main():
    """Monitor and display hackerspace statuses."""
    
    console.print(Panel.fit("Hackerspace Status Monitor", style="bold blue"))
    
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
        
        # Step 2: Fetch space statuses (limit to first 30 for demo)
        task2 = progress.add_task("Fetching space statuses...", total=30)
        space_urls = list(directory.spaces.values())[:30]  # Limit for demo
        
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
    
    # Get opening patterns analysis
    opening_patterns = analyzer.analyze_opening_patterns()
    
    # Display summary
    console.print("\n[bold]Status Summary:[/bold]")
    console.print(f"• Total spaces with status: {opening_patterns['total_with_status']}")
    console.print(f"• Currently open: {opening_patterns['open_count']}")
    console.print(f"• Currently closed: {opening_patterns['closed_count']}")
    console.print(f"• Recent status changes (24h): {opening_patterns['recent_changes']}")
    
    # Display open spaces
    if opening_patterns['open_spaces']:
        console.print(f"\n[green]Currently Open Spaces ({len(opening_patterns['open_spaces'])}):[/green]")
        for space_name in opening_patterns['open_spaces'][:10]:  # Show first 10
            console.print(f"  • {space_name}")
        if len(opening_patterns['open_spaces']) > 10:
            console.print(f"  ... and {len(opening_spaces) - 10} more")
    
    # Create detailed status table
    console.print("\n")
    status_table = create_status_table(spaces_data)
    console.print(status_table)
    
    # Additional analysis
    contact_analysis = analyzer.analyze_contact_methods()
    if contact_analysis.get('spaces_with_contact', 0) > 0:
        console.print(f"\n[bold]Contact Methods:[/bold]")
        for method, count in contact_analysis['contact_methods'].items():
            percentage = contact_analysis['contact_percentages'][method]
            console.print(f"• {method}: {count} spaces ({percentage:.1f}%)")
    
    # Find spaces with sensors
    spaces_with_sensors = analyzer.find_spaces_by_criteria(has_sensors=True)
    if spaces_with_sensors:
        console.print(f"\n[bold]Spaces with Sensors ({len(spaces_with_sensors)}):[/bold]")
        for space in spaces_with_sensors[:5]:  # Show first 5
            sensor_count = sum(len(sensors) for sensors in space.sensors.values()) if space.sensors else 0
            console.print(f"  • {space.space} - {sensor_count} sensors")
    
    console.print(Panel.fit("Status monitoring complete!", style="bold green"))


if __name__ == "__main__":
    main()
