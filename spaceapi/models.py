"""
Data models for SpaceAPI schema using Pydantic for validation and serialization.
"""

from typing import Dict, List, Optional, Union, Any
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl, validator, root_validator


class SpaceContact(BaseModel):
    """Contact information for a hackerspace."""
    email: Optional[str] = None
    irc: Optional[str] = None
    ml: Optional[str] = None
    twitter: Optional[str] = None
    facebook: Optional[str] = None
    mastodon: Optional[str] = None
    phone: Optional[str] = None
    sip: Optional[str] = None
    jabber: Optional[str] = None
    issue_mail: Optional[str] = None


class SpaceLocation(BaseModel):
    """Location information for a hackerspace."""
    address: Optional[str] = None
    lat: Optional[float] = Field(None, ge=-90, le=90)
    lon: Optional[float] = Field(None, ge=-180, le=180)
    timezone: Optional[str] = None


class SpaceStateIcon(BaseModel):
    """Icons showing space status."""
    open: HttpUrl
    closed: HttpUrl


class SpaceState(BaseModel):
    """Current state information for a hackerspace."""
    open: Optional[bool] = None
    lastchange: Optional[Union[int, float]] = None
    trigger_person: Optional[str] = None
    message: Optional[str] = None
    icon: Optional[SpaceStateIcon] = None

    @validator('lastchange', pre=True)
    def validate_timestamp(cls, v):
        if v is not None:
            # Convert float timestamps to int
            if isinstance(v, float):
                v = int(v)
            # Basic validation - just check it's not obviously wrong
            if v < 0:
                return None  # Invalid timestamp, return None instead of raising error
        return v


class SpaceEvent(BaseModel):
    """Recent event in the hackerspace."""
    name: str
    type: Optional[str] = None
    timestamp: Optional[int] = None
    extra: Optional[Union[Dict[str, Any], str]] = None  # Allow string for older API versions


class SpaceProject(BaseModel):
    """Project associated with the hackerspace."""
    name: Optional[str] = None
    url: HttpUrl
    description: Optional[str] = None
    type: Optional[str] = None


class SpaceArea(BaseModel):
    """Physical area within the hackerspace."""
    name: str
    description: Optional[str] = None
    square_meters: float = Field(..., gt=0)


class SpaceSensor(BaseModel):
    """Sensor data from the hackerspace."""
    name: Optional[str] = None  # Make name optional for older API versions
    unit: Optional[str] = None
    value: Optional[Union[float, int, str, None]] = None  # Allow None values
    location: Optional[str] = None
    names: Optional[List[str]] = None
    timestamp: Optional[int] = None


class SpaceStatus(BaseModel):
    """Complete SpaceAPI status for a hackerspace."""
    # Handle different API versions - make api_compatibility optional and support 'api' field
    api_compatibility: Optional[List[str]] = None
    api: Optional[str] = None  # For older API versions
    space: str
    logo: Optional[HttpUrl] = None
    url: Optional[HttpUrl] = None
    location: Optional[SpaceLocation] = None
    contact: Optional[SpaceContact] = None
    issue_report_channels: Optional[List[str]] = None
    state: Optional[SpaceState] = None
    events: Optional[List[SpaceEvent]] = None
    projects: Optional[List[Union[HttpUrl, SpaceProject]]] = None
    spacefed: Optional[Dict[str, bool]] = None
    cam: Optional[List[HttpUrl]] = None
    feed: Optional[Dict[str, HttpUrl]] = None
    radio_show: Optional[List[HttpUrl]] = None
    cache: Optional[Dict[str, Any]] = None
    projects_url: Optional[HttpUrl] = None
    sensors: Optional[Dict[str, List[Union[SpaceSensor, Dict[str, Any], None]]]] = None  # More flexible sensors
    links: Optional[List[Dict[str, Any]]] = None
    icon: Optional[SpaceStateIcon] = None
    times: Optional[Dict[str, Any]] = None

    @root_validator(pre=True)
    def handle_api_versions(cls, values):
        """Handle different API versions and field names."""
        # Handle 'api' field for older versions
        if 'api' in values and 'api_compatibility' not in values:
            api_version = values.pop('api')
            if api_version:
                values['api_compatibility'] = [api_version]
        
        # Ensure we have at least one version field
        if not values.get('api_compatibility') and not values.get('api'):
            # Default to v14 if no version specified
            values['api_compatibility'] = ['14']
        
        return values

    @validator('sensors', pre=True)
    def validate_sensors(cls, v):
        """Handle flexible sensor data from different API versions."""
        if v is None:
            return None
        
        cleaned_sensors = {}
        for sensor_type, sensors in v.items():
            if sensors is None:
                continue
            
            cleaned_sensor_list = []
            for sensor in sensors:
                if sensor is None:
                    continue
                
                # Handle dict sensors that might not match our model
                if isinstance(sensor, dict):
                    # Filter out None values and ensure required fields have defaults
                    cleaned_sensor = {k: v for k, v in sensor.items() if v is not None}
                    if 'name' not in cleaned_sensor:
                        cleaned_sensor['name'] = f"{sensor_type}_sensor"
                    cleaned_sensor_list.append(cleaned_sensor)
                else:
                    cleaned_sensor_list.append(sensor)
            
            if cleaned_sensor_list:
                cleaned_sensors[sensor_type] = cleaned_sensor_list
        
        return cleaned_sensors if cleaned_sensors else None


class SpaceDirectory(BaseModel):
    """Directory of hackerspaces from SpaceAPI."""
    spaces: Dict[str, HttpUrl] = Field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "SpaceDirectory":
        """Create SpaceDirectory from a dictionary mapping space names to URLs."""
        spaces = {}
        for name, url in data.items():
            spaces[name] = HttpUrl(url)
        return cls(spaces=spaces)

    def get_open_spaces(self) -> List[str]:
        """Get list of space names that are currently open."""
        # This would require fetching all space statuses
        # For now, return empty list as placeholder
        return []

    def get_spaces_by_country(self) -> Dict[str, List[str]]:
        """Group spaces by country (requires fetching location data)."""
        # This would require fetching all space statuses
        # For now, return empty dict as placeholder
        return {}
