"""
SpaceAPI Explorer

A Python library for exploring the global state of hackerspaces using the SpaceAPI directory.
"""

from .client import SpaceAPIClient
from .models import SpaceDirectory, SpaceStatus

__version__ = "0.1.0"
__all__ = ["SpaceAPIClient", "SpaceDirectory", "SpaceStatus"]
