"""
SpaceAPI client for fetching directory and space status data.
"""

import json
import logging
from typing import Dict, List, Optional, Union
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .models import SpaceDirectory, SpaceStatus


class SpaceAPIClient:
    """Client for interacting with the SpaceAPI directory and individual space endpoints."""
    
    def __init__(self, directory_url: str = "https://directory.spaceapi.io/", 
                 timeout: int = 30, max_retries: int = 3):
        """
        Initialize the SpaceAPI client.
        
        Args:
            directory_url: URL of the SpaceAPI directory
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self.directory_url = directory_url
        self.timeout = timeout
        self.session = self._create_session(max_retries)
        self.logger = logging.getLogger(__name__)
    
    def _create_session(self, max_retries: int) -> requests.Session:
        """Create a requests session with retry strategy."""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        session.headers.update({
            'User-Agent': 'SpaceAPI-Explorer/0.1.0'
        })
        
        return session
    
    def get_directory(self, force_refresh: bool = False) -> SpaceDirectory:
        """
        Fetch the SpaceAPI directory.
        
        Args:
            force_refresh: If True, bypass any caching
            
        Returns:
            SpaceDirectory object containing all known spaces
            
        Raises:
            requests.RequestException: If the request fails
        """
        try:
            response = self.session.get(
                self.directory_url,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            directory_data = response.json()
            return SpaceDirectory.from_dict(directory_data)
            
        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch directory: {e}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in directory response: {e}")
            raise
    
    def get_space_status(self, space_url: str) -> Optional[SpaceStatus]:
        """
        Fetch status information for a specific hackerspace.
        
        Args:
            space_url: URL of the space's SpaceAPI endpoint
            
        Returns:
            SpaceStatus object or None if request fails
            
        Raises:
            requests.RequestException: If the request fails
        """
        try:
            response = self.session.get(space_url, timeout=self.timeout)
            response.raise_for_status()
            
            space_data = response.json()
            return SpaceStatus(**space_data)
            
        except requests.RequestException as e:
            self.logger.warning(f"Failed to fetch space status from {space_url}: {e}")
            return None
        except (json.JSONDecodeError, ValueError) as e:
            self.logger.warning(f"Invalid response from {space_url}: {e}")
            return None
        except Exception as e:
            # Catch Pydantic validation errors and other exceptions
            self.logger.warning(f"Validation error for {space_url}: {e}")
            return None
    
    def get_multiple_space_statuses(self, space_urls: List[str], 
                                  max_concurrent: int = 10) -> Dict[str, Optional[SpaceStatus]]:
        """
        Fetch status information for multiple hackerspaces concurrently.
        
        Args:
            space_urls: List of space URLs to fetch
            max_concurrent: Maximum number of concurrent requests
            
        Returns:
            Dictionary mapping URLs to SpaceStatus objects (or None if failed)
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        results = {}
        
        def fetch_space(url: str) -> tuple[str, Optional[SpaceStatus]]:
            return url, self.get_space_status(url)
        
        with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            future_to_url = {
                executor.submit(fetch_space, url): url 
                for url in space_urls
            }
            
            for future in as_completed(future_to_url):
                url, status = future.result()
                results[url] = status
        
        return results
    
    def search_spaces(self, query: str, search_field: str = "name") -> List[str]:
        """
        Search for spaces by name or other criteria.
        
        Args:
            query: Search query string
            search_field: Field to search in ("name" currently supported)
            
        Returns:
            List of matching space URLs
        """
        directory = self.get_directory()
        query_lower = query.lower()
        
        if search_field == "name":
            matching_urls = [
                str(url) for name, url in directory.spaces.items()
                if query_lower in name.lower()
            ]
        else:
            raise ValueError(f"Unsupported search field: {search_field}")
        
        return matching_urls
    
    def get_directory_stats(self) -> Dict[str, Union[int, List[str]]]:
        """
        Get basic statistics about the SpaceAPI directory.
        
        Returns:
            Dictionary with directory statistics
        """
        directory = self.get_directory()
        
        stats = {
            "total_spaces": len(directory.spaces),
            "last_updated": datetime.now().isoformat(),
        }
        
        # Extract some basic info from space names
        space_names = list(directory.spaces.keys())
        stats["sample_spaces"] = space_names[:10]  # First 10 spaces as sample
        
        return stats
    
    def close(self):
        """Close the HTTP session."""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
