#!/usr/bin/env python3
"""
API Health Monitor - Check the health and availability of SpaceAPI endpoints.
This utility helps identify broken, deprecated, or problematic endpoints in the directory.
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Any
from collections import defaultdict
import time

# Add the parent directory to the path so we can import spaceapi
sys.path.insert(0, str(Path(__file__).parent.parent))

from spaceapi import SpaceAPIClient
from spaceapi.analyzer import SpaceAnalyzer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.tree import Tree
from rich.text import Text

console = Console()


class HealthMonitor:
    """Monitor the health of SpaceAPI endpoints."""
    
    def __init__(self):
        self.client = SpaceAPIClient()
        self.results = {
            'total': 0,
            'successful': 0,
            'failed': 0,
            'errors': defaultdict(list),
            'response_times': [],
            'api_versions': defaultdict(int),
            'issues': []
        }
    
    def check_endpoint_health(self, space_url: str, space_name: str) -> Dict[str, Any]:
        """Check the health of a single SpaceAPI endpoint."""
        start_time = time.time()
        
        try:
            response = self.client.session.get(space_url, timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    return {
                        'status': 'success',
                        'response_time': response_time,
                        'status_code': response.status_code,
                        'data_size': len(str(data)),
                        'api_version': self._extract_api_version(data),
                        'has_state': 'state' in data,
                        'has_location': 'location' in data,
                        'has_sensors': 'sensors' in data,
                        'space_name': space_name,
                        'url': space_url
                    }
                except Exception as e:
                    return {
                        'status': 'invalid_json',
                        'response_time': response_time,
                        'status_code': response.status_code,
                        'error': str(e),
                        'space_name': space_name,
                        'url': space_url
                    }
            else:
                return {
                    'status': 'http_error',
                    'response_time': response_time,
                    'status_code': response.status_code,
                    'space_name': space_name,
                    'url': space_url
                }
                
        except Exception as e:
            return {
                'status': 'connection_error',
                'response_time': time.time() - start_time,
                'error': str(e),
                'space_name': space_name,
                'url': space_url
            }
    
    def _extract_api_version(self, data: Dict) -> str:
        """Extract API version from response data."""
        if 'api_compatibility' in data and data['api_compatibility']:
            return ','.join(data['api_compatibility'])
        elif 'api' in data:
            return data['api']
        else:
            return 'unknown'
    
    def run_health_check(self, max_spaces: int = 50) -> Dict[str, Any]:
        """Run comprehensive health check on SpaceAPI endpoints."""
        console.print(Panel.fit("SpaceAPI Health Monitor", style="bold blue"))
        
        # Get directory
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            
            task = progress.add_task("Fetching SpaceAPI directory...", total=None)
            try:
                directory = self.client.get_directory()
                progress.update(task, description=f"Directory fetched: {len(directory.spaces)} spaces")
            except Exception as e:
                console.print(f"[red]Error fetching directory: {e}[/red]")
                return self.results
            
            # Limit spaces for demo
            space_items = list(directory.spaces.items())[:max_spaces]
            
            # Check each endpoint
            task2 = progress.add_task("Checking endpoint health...", total=len(space_items))
            
            for space_name, space_url in space_items:
                result = self.check_endpoint_health(str(space_url), space_name)
                
                self.results['total'] += 1
                self.results['response_times'].append(result['response_time'])
                
                if result['status'] == 'success':
                    self.results['successful'] += 1
                    self.results['api_versions'][result['api_version']] += 1
                else:
                    self.results['failed'] += 1
                    self.results['errors'][result['status']].append(result)
                
                progress.update(task2, advance=1)
        
        return self.results
    
    def generate_health_report(self, results: Dict[str, Any]) -> None:
        """Generate a comprehensive health report."""
        console.print("\n[bold]🏥 SpaceAPI Health Report[/bold]")
        
        # Summary statistics
        success_rate = (results['successful'] / results['total'] * 100) if results['total'] > 0 else 0
        avg_response_time = sum(results['response_times']) / len(results['response_times']) if results['response_times'] else 0
        
        console.print(f"\n[bold]📊 Summary Statistics:[/bold]")
        console.print(f"• Total endpoints checked: {results['total']}")
        console.print(f"• Successful: {results['successful']} ({success_rate:.1f}%)")
        console.print(f"• Failed: {results['failed']} ({100-success_rate:.1f}%)")
        console.print(f"• Average response time: {avg_response_time:.2f}s")
        
        # API version distribution
        if results['api_versions']:
            console.print(f"\n[bold]🔢 API Version Distribution:[/bold]")
            for version, count in sorted(results['api_versions'].items()):
                percentage = (count / results['successful'] * 100) if results['successful'] > 0 else 0
                console.print(f"• v{version}: {count} spaces ({percentage:.1f}%)")
        
        # Error breakdown
        if results['errors']:
            console.print(f"\n[bold]❌ Error Breakdown:[/bold]")
            for error_type, errors in results['errors'].items():
                console.print(f"• {error_type}: {len(errors)} endpoints")
        
        # Detailed issues table
        self._show_issues_table(results)
        
        # Recommendations
        self._show_recommendations(results)
    
    def _show_issues_table(self, results: Dict[str, Any]) -> None:
        """Show detailed issues in a table."""
        if not results['errors']:
            return
        
        table = Table(title="🔍 Detailed Issues")
        table.add_column("Space", style="cyan")
        table.add_column("Status", style="red")
        table.add_column("Details", style="dim")
        table.add_column("Response Time", justify="right")
        
        for error_type, errors in results['errors'].items():
            for error in errors[:10]:  # Limit to first 10 per error type
                status_text = error_type.replace('_', ' ').title()
                details = error.get('error', f"HTTP {error.get('status_code', 'N/A')}")
                response_time = f"{error['response_time']:.2f}s"
                
                table.add_row(
                    error['space_name'][:30],
                    status_text,
                    details[:50],
                    response_time
                )
        
        console.print(table)
    
    def _show_recommendations(self, results: Dict[str, Any]) -> None:
        """Show recommendations based on health check results."""
        console.print(f"\n[bold]💡 Recommendations:[/bold]")
        
        success_rate = (results['successful'] / results['total'] * 100) if results['total'] > 0 else 0
        
        if success_rate < 80:
            console.print("• [yellow]Overall health is concerning. Consider directory cleanup.[/yellow]")
        elif success_rate < 95:
            console.print("• [yellow]Some endpoints need attention. Regular maintenance recommended.[/yellow]")
        else:
            console.print("• [green]Overall health is good![/green]")
        
        # Specific recommendations
        if 'connection_error' in results['errors']:
            console.print(f"• {len(results['errors']['connection_error'])} spaces have connection issues - check if they're still active")
        
        if 'http_error' in results['errors']:
            console.print(f"• {len(results['errors']['http_error'])} spaces return HTTP errors - may need URL updates")
        
        if 'invalid_json' in results['errors']:
            console.print(f"• {len(results['errors']['invalid_json'])} spaces have invalid JSON - schema validation needed")
        
        # API version recommendations
        old_versions = [v for v in results['api_versions'].keys() if v.startswith('0.13')]
        if old_versions:
            console.print(f"• {sum(results['api_versions'][v] for v in old_versions)} spaces use older API versions - consider upgrades")
    
    def export_report(self, results: Dict[str, Any], filename: str = None) -> None:
        """Export health report to a file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"health_report_{timestamp}.json"
        
        import json
        
        # Convert defaultdict to regular dicts for JSON serialization
        export_data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'summary': {
                'total': results['total'],
                'successful': results['successful'],
                'failed': results['failed'],
                'success_rate': (results['successful'] / results['total'] * 100) if results['total'] > 0 else 0,
                'avg_response_time': sum(results['response_times']) / len(results['response_times']) if results['response_times'] else 0
            },
            'api_versions': dict(results['api_versions']),
            'errors': {k: v for k, v in results['errors'].items()},
            'all_response_times': results['response_times']
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        console.print(f"\n[green]📄 Report exported to {filename}[/green]")


def main():
    """Run the SpaceAPI health monitor."""
    monitor = HealthMonitor()
    
    # Run health check
    results = monitor.run_health_check(max_spaces=50)  # Limit for demo
    
    # Generate report
    monitor.generate_health_report(results)
    
    # Export report
    monitor.export_report(results)
    
    console.print(Panel.fit("Health monitoring complete!", style="bold green"))


if __name__ == "__main__":
    main()
