"""
Visualization tools for SpaceAPI data.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import folium
from typing import Dict, List, Optional, Any
import pandas as pd
from datetime import datetime

from .models import SpaceStatus


class SpaceVisualizer:
    """Create visualizations for SpaceAPI data."""
    
    def __init__(self, style: str = "seaborn-v0_8"):
        """Initialize visualizer with plotting style."""
        plt.style.use(style)
        sns.set_palette("husl")
    
    def plot_opening_status_pie(self, spaces_data: List[SpaceStatus], 
                               save_path: Optional[str] = None) -> None:
        """Create a pie chart of opening vs closed spaces."""
        open_count = sum(1 for space in spaces_data 
                        if space.state and space.state.open is True)
        closed_count = sum(1 for space in spaces_data 
                          if space.state and space.state.open is False)
        unknown_count = len(spaces_data) - open_count - closed_count
        
        if open_count + closed_count == 0:
            print("No space status data available for plotting")
            return
        
        labels = []
        sizes = []
        colors = []
        
        if open_count > 0:
            labels.append(f'Open ({open_count})')
            sizes.append(open_count)
            colors.append('#2ecc71')
        
        if closed_count > 0:
            labels.append(f'Closed ({closed_count})')
            sizes.append(closed_count)
            colors.append('#e74c3c')
        
        if unknown_count > 0:
            labels.append(f'Unknown ({unknown_count})')
            sizes.append(unknown_count)
            colors.append('#95a5a6')
        
        fig, ax = plt.subplots(figsize=(10, 8))
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, 
                                         autopct='%1.1f%%', startangle=90)
        
        ax.set_title('Hackerspace Opening Status Distribution', 
                    fontsize=16, fontweight='bold', pad=20)
        
        # Make percentage text more readable
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
    
    def plot_geographic_distribution(self, spaces_data: List[SpaceStatus], 
                                   save_path: Optional[str] = None) -> None:
        """Create a scatter plot of hackerspace locations."""
        locations = []
        for space in spaces_data:
            if space.location and space.location.lat and space.location.lon:
                locations.append({
                    'name': space.space,
                    'lat': space.location.lat,
                    'lon': space.location.lon,
                    'open': space.state.open if space.state else None
                })
        
        if not locations:
            print("No location data available for plotting")
            return
        
        df = pd.DataFrame(locations)
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Color by status
        colors = []
        for _, row in df.iterrows():
            if row['open'] is True:
                colors.append('#2ecc71')  # Green for open
            elif row['open'] is False:
                colors.append('#e74c3c')  # Red for closed
            else:
                colors.append('#95a5a6')  # Gray for unknown
        
        ax.scatter(df['lon'], df['lat'], c=colors, alpha=0.7, s=50)
        
        ax.set_xlabel('Longitude', fontsize=12)
        ax.set_ylabel('Latitude', fontsize=12)
        ax.set_title('Global Hackerspace Distribution', fontsize=16, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#2ecc71', label='Open'),
            Patch(facecolor='#e74c3c', label='Closed'),
            Patch(facecolor='#95a5a6', label='Unknown')
        ]
        ax.legend(handles=legend_elements, loc='upper right')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
    
    def plot_contact_methods(self, spaces_data: List[SpaceStatus], 
                           save_path: Optional[str] = None) -> None:
        """Create a bar chart of contact methods used by hackerspaces."""
        contact_methods = {
            'email': 0,
            'irc': 0,
            'twitter': 0,
            'mastodon': 0,
            'facebook': 0,
            'phone': 0
        }
        
        for space in spaces_data:
            if space.contact:
                if space.contact.email:
                    contact_methods['email'] += 1
                if space.contact.irc:
                    contact_methods['irc'] += 1
                if space.contact.twitter:
                    contact_methods['twitter'] += 1
                if space.contact.mastodon:
                    contact_methods['mastodon'] += 1
                if space.contact.facebook:
                    contact_methods['facebook'] += 1
                if space.contact.phone:
                    contact_methods['phone'] += 1
        
        # Remove methods with zero count
        contact_methods = {k: v for k, v in contact_methods.items() if v > 0}
        
        if not contact_methods:
            print("No contact method data available for plotting")
            return
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        methods = list(contact_methods.keys())
        counts = list(contact_methods.values())
        
        bars = ax.bar(methods, counts, color='skyblue', edgecolor='navy', alpha=0.7)
        
        ax.set_xlabel('Contact Method', fontsize=12)
        ax.set_ylabel('Number of Spaces', fontsize=12)
        ax.set_title('Contact Methods Used by Hackerspaces', fontsize=16, fontweight='bold')
        
        # Add value labels on bars
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                   f'{count}', ha='center', va='bottom')
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
    
    def create_world_map(self, spaces_data: List[SpaceStatus], 
                        save_path: Optional[str] = None) -> folium.Map:
        """Create an interactive world map of hackerspaces."""
        # Create map centered on world
        m = folium.Map(location=[20, 0], zoom_start=2)
        
        locations = []
        for space in spaces_data:
            if space.location and space.location.lat and space.location.lon:
                locations.append({
                    'name': space.space,
                    'lat': space.location.lat,
                    'lon': space.location.lon,
                    'address': space.location.address,
                    'url': str(space.url) if space.url else None,
                    'open': space.state.open if space.state else None
                })
        
        if not locations:
            print("No location data available for mapping")
            return m
        
        # Add markers for each space
        for loc in locations:
            # Determine marker color based on status
            if loc['open'] is True:
                color = 'green'
                icon = 'check'
            elif loc['open'] is False:
                color = 'red'
                icon = 'times'
            else:
                color = 'gray'
                icon = 'question'
            
            # Create popup content
            popup_content = f"""
            <b>{loc['name']}</b><br>
            {loc['address'] or 'No address'}<br>
            Status: {'Open' if loc['open'] is True else 'Closed' if loc['open'] is False else 'Unknown'}<br>
            {f'<a href="{loc["url"]}" target="_blank">Website</a>' if loc['url'] else ''}
            """
            
            folium.Marker(
                location=[loc['lat'], loc['lon']],
                popup=folium.Popup(popup_content, max_width=300),
                tooltip=loc['name'],
                icon=folium.Icon(color=color, icon=icon, prefix='fa')
            ).add_to(m)
        
        # Add legend
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 150px; height: 90px; 
                    background-color:white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <h4>Status Legend</h4>
        <i class="fa fa-check-circle" style="color:green"></i> Open<br>
        <i class="fa fa-times-circle" style="color:red"></i> Closed<br>
        <i class="fa fa-question-circle" style="color:gray"></i> Unknown
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        if save_path:
            m.save(save_path)
        
        return m
    
    def plot_sensor_distribution(self, spaces_data: List[SpaceStatus], 
                                save_path: Optional[str] = None) -> None:
        """Create a bar chart of sensor types across hackerspaces."""
        sensor_counts = {}
        
        for space in spaces_data:
            if space.sensors:
                for sensor_type, sensors in space.sensors.items():
                    sensor_counts[sensor_type] = sensor_counts.get(sensor_type, 0) + len(sensors)
        
        if not sensor_counts:
            print("No sensor data available for plotting")
            return
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        sensor_types = list(sensor_counts.keys())
        counts = list(sensor_counts.values())
        
        bars = ax.bar(sensor_types, counts, color='lightcoral', edgecolor='darkred', alpha=0.7)
        
        ax.set_xlabel('Sensor Type', fontsize=12)
        ax.set_ylabel('Total Count', fontsize=12)
        ax.set_title('Sensor Types Across Hackerspaces', fontsize=16, fontweight='bold')
        
        # Add value labels on bars
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   f'{count}', ha='center', va='bottom')
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
    
    def plot_api_versions(self, spaces_data: List[SpaceStatus], 
                         save_path: Optional[str] = None) -> None:
        """Create a bar chart of API compatibility versions."""
        version_counts = {}
        
        for space in spaces_data:
            if space.api_compatibility:
                for version in space.api_compatibility:
                    version_counts[version] = version_counts.get(version, 0) + 1
        
        if not version_counts:
            print("No API version data available for plotting")
            return
        
        fig, ax = plt.subplots(figsize=(8, 6))
        
        versions = list(version_counts.keys())
        counts = list(version_counts.values())
        
        bars = ax.bar(versions, counts, color='gold', edgecolor='orange', alpha=0.7)
        
        ax.set_xlabel('API Version', fontsize=12)
        ax.set_ylabel('Number of Spaces', fontsize=12)
        ax.set_title('SpaceAPI Version Distribution', fontsize=16, fontweight='bold')
        
        # Add value labels on bars
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   f'{count}', ha='center', va='bottom')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
