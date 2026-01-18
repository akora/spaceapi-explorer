"""
Data analysis tools for SpaceAPI data.
"""

import json
from typing import Dict, List, Optional, Tuple, Any
from collections import Counter, defaultdict
from datetime import datetime, timezone
import pandas as pd
import numpy as np

from .models import SpaceStatus, SpaceDirectory


class SpaceAnalyzer:
    """Analyze SpaceAPI data to extract insights about global hackerspaces."""
    
    def __init__(self):
        self.spaces_data: List[SpaceStatus] = []
        self.directory: Optional[SpaceDirectory] = None
    
    def load_spaces(self, spaces_data: List[SpaceStatus]):
        """Load space status data for analysis."""
        self.spaces_data = spaces_data
    
    def load_directory(self, directory: SpaceDirectory):
        """Load directory data for analysis."""
        self.directory = directory
    
    def get_basic_stats(self) -> Dict[str, Any]:
        """Get basic statistics about the loaded spaces."""
        if not self.spaces_data:
            return {"error": "No space data loaded"}
        
        total_spaces = len(self.spaces_data)
        spaces_with_location = sum(1 for space in self.spaces_data if space.location)
        spaces_with_state = sum(1 for space in self.spaces_data if space.state)
        spaces_open = sum(1 for space in self.spaces_data 
                         if space.state and space.state.open is True)
        
        return {
            "total_spaces": total_spaces,
            "spaces_with_location": spaces_with_location,
            "spaces_with_state": spaces_with_state,
            "currently_open": spaces_open,
            "open_percentage": (spaces_open / spaces_with_state * 100) if spaces_with_state > 0 else 0,
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
    
    def analyze_geographic_distribution(self) -> Dict[str, Any]:
        """Analyze geographic distribution of hackerspaces."""
        if not self.spaces_data:
            return {"error": "No space data loaded"}
        
        locations = []
        for space in self.spaces_data:
            if space.location and space.location.lat and space.location.lon:
                locations.append({
                    "name": space.space,
                    "lat": space.location.lat,
                    "lon": space.location.lon,
                    "address": space.location.address
                })
        
        # Group by approximate regions (very rough grouping)
        regions = defaultdict(list)
        for loc in locations:
            lat, lon = loc["lat"], loc["lon"]
            
            # Very rough continental grouping
            if lat > 60:  # Northern regions
                region = "Arctic"
            elif 30 <= lat <= 60:
                if -140 <= lon <= -40:  # Americas
                    region = "North America"
                elif -10 <= lon <= 40:  # Europe/Africa
                    if lat > 0:
                        region = "Europe"
                    else:
                        region = "North Africa"
                else:  # Asia
                    region = "Asia"
            elif -30 <= lat <= 30:  # Tropical regions
                if -80 <= lon <= -30:  # South America
                    region = "South America"
                elif -20 <= lon <= 50:  # Africa/Middle East
                    region = "Africa/Middle East"
                else:  # Asia-Pacific
                    region = "Asia-Pacific"
            else:  # Southern regions
                region = "Southern Hemisphere"
            
            regions[region].append(loc)
        
        return {
            "total_locations": len(locations),
            "regions": {region: len(spaces) for region, spaces in regions.items()},
            "locations": locations
        }
    
    def analyze_opening_patterns(self) -> Dict[str, Any]:
        """Analyze opening patterns and status changes."""
        if not self.spaces_data:
            return {"error": "No space data loaded"}
        
        status_data = []
        now = datetime.now(timezone.utc).timestamp()
        
        for space in self.spaces_data:
            if space.state:
                status_info = {
                    "name": space.space,
                    "open": space.state.open,
                    "lastchange": space.state.lastchange,
                    "message": space.state.message
                }
                
                # Calculate time since last change
                if space.state.lastchange:
                    hours_since_change = (now - space.state.lastchange) / 3600
                    status_info["hours_since_change"] = hours_since_change
                
                status_data.append(status_info)
        
        # Analyze opening patterns
        open_spaces = [s for s in status_data if s["open"] is True]
        closed_spaces = [s for s in status_data if s["open"] is False]
        
        # Analyze last change times
        recent_changes = [s for s in status_data if s.get("hours_since_change", 0) < 24]
        
        return {
            "total_with_status": len(status_data),
            "open_count": len(open_spaces),
            "closed_count": len(closed_spaces),
            "recent_changes": len(recent_changes),
            "open_spaces": [s["name"] for s in open_spaces],
            "status_details": status_data
        }
    
    def analyze_contact_methods(self) -> Dict[str, Any]:
        """Analyze contact methods used by hackerspaces."""
        if not self.spaces_data:
            return {"error": "No space data loaded"}
        
        contact_methods = defaultdict(int)
        spaces_with_contact = 0
        
        for space in self.spaces_data:
            if space.contact:
                spaces_with_contact += 1
                if space.contact.email:
                    contact_methods["email"] += 1
                if space.contact.irc:
                    contact_methods["irc"] += 1
                if space.contact.twitter:
                    contact_methods["twitter"] += 1
                if space.contact.mastodon:
                    contact_methods["mastodon"] += 1
                if space.contact.facebook:
                    contact_methods["facebook"] += 1
                if space.contact.phone:
                    contact_methods["phone"] += 1
        
        return {
            "spaces_with_contact": spaces_with_contact,
            "contact_methods": dict(contact_methods),
            "contact_percentages": {
                method: (count / spaces_with_contact * 100) if spaces_with_contact > 0 else 0
                for method, count in contact_methods.items()
            }
        }
    
    def analyze_sensor_data(self) -> Dict[str, Any]:
        """Analyze sensor data from hackerspaces."""
        if not self.spaces_data:
            return {"error": "No space data loaded"}
        
        sensor_types = defaultdict(int)
        spaces_with_sensors = 0
        sensor_examples = defaultdict(list)
        
        for space in self.spaces_data:
            if space.sensors:
                spaces_with_sensors += 1
                for sensor_type, sensors in space.sensors.items():
                    sensor_types[sensor_type] += len(sensors)
                    # Store a few examples of each sensor type
                    for sensor in sensors[:2]:  # Limit to 2 examples per space
                        sensor_examples[sensor_type].append({
                            "space": space.space,
                            "name": sensor.name,
                            "unit": sensor.unit,
                            "value": sensor.value
                        })
        
        return {
            "spaces_with_sensors": spaces_with_sensors,
            "sensor_types": dict(sensor_types),
            "total_sensors": sum(sensor_types.values()),
            "sensor_examples": dict(sensor_examples)
        }
    
    def export_to_dataframe(self) -> pd.DataFrame:
        """Export space data to a pandas DataFrame for further analysis."""
        if not self.spaces_data:
            return pd.DataFrame()
        
        data = []
        for space in self.spaces_data:
            row = {
                "name": space.space,
                "url": str(space.url) if space.url else None,
                "logo": str(space.logo) if space.logo else None,
                "lat": space.location.lat if space.location else None,
                "lon": space.location.lon if space.location else None,
                "address": space.location.address if space.location else None,
                "timezone": space.location.timezone if space.location else None,
                "open": space.state.open if space.state else None,
                "lastchange": space.state.lastchange if space.state else None,
                "has_contact": space.contact is not None,
                "has_sensors": space.sensors is not None,
                "has_projects": space.projects is not None,
                "api_version": space.api_compatibility[0] if space.api_compatibility else None
            }
            data.append(row)
        
        return pd.DataFrame(data)
    
    def find_spaces_by_criteria(self, **criteria) -> List[SpaceStatus]:
        """Find spaces matching specific criteria."""
        if not self.spaces_data:
            return []
        
        matching_spaces = []
        
        for space in self.spaces_data:
            matches = True
            
            # Check each criterion
            for key, value in criteria.items():
                if key == "open" and space.state:
                    if space.state.open != value:
                        matches = False
                        break
                elif key == "has_location" and value is True:
                    if not space.location:
                        matches = False
                        break
                elif key == "has_sensors" and value is True:
                    if not space.sensors:
                        matches = False
                        break
                elif key == "name_contains" and isinstance(value, str):
                    if value.lower() not in space.space.lower():
                        matches = False
                        break
            
            if matches:
                matching_spaces.append(space)
        
        return matching_spaces
