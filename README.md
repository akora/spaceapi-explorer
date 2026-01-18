# SpaceAPI Explorer

A Python toolkit for exploring the global hackerspace ecosystem through the SpaceAPI directory.

## What is SpaceAPI?

SpaceAPI is a standardized JSON schema used by hackerspaces, makerspaces, and fablabs worldwide to share real-time information about their status, location, events, and sensors.

## Features

- 🌍 **Global Directory Access** - Fetch data from 240+ hackerspaces
- 📊 **Real-time Status** - Monitor open/closed states and recent changes
- 📈 **Data Analysis** - Geographic distribution, contact patterns, sensor data
- 🗺️ **Interactive Maps** - Visualize space locations worldwide
- 🔍 **Flexible Search** - Find spaces by name, location, or status
- 📦 **Version Agnostic** - Supports SpaceAPI v0.13 through v15

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run examples
python examples/directory_stats.py    # Directory overview
python examples/status_monitor.py     # Real-time status monitor
python examples/world_map.py          # Interactive world map
python examples/health_monitor.py      # API health checker
```

## Usage

```python
from spaceapi import SpaceAPIClient

# Initialize client
client = SpaceAPIClient()

# Get directory
directory = client.get_directory()
print(f"Found {len(directory.spaces)} hackerspaces")

# Get specific space status
status = client.get_space_status("https://metalab-spaceapi.melina.jetzt/v15")
print(f"Metalab is {'open' if status.state.open else 'closed'}")
```

## Project Structure

```text
spaceapi/
├── client.py     # HTTP client with retry logic
├── models.py     # Pydantic models for API validation  
├── analyzer.py   # Data analysis utilities
└── visualizer.py # Charts and interactive maps

examples/
├── directory_stats.py   # Directory statistics
├── status_monitor.py    # Status monitoring
├── world_map.py         # Geographic visualization
└── health_monitor.py    # API health checker
```

## Data Sources

- **Directory**: [directory.spaceapi.io](https://directory.spaceapi.io/)
- **Documentation**: [spaceapi.io](https://spaceapi.io/)
- **Community**: IRC #spaceapi on Libera.chat

## For Hackerspace Operators

Are you a hackerspace operator who wants to get listed? Check out our **[Hackerspace Guide](docs/HACKERSPACE_GUIDE.md)** for a quick tutorial on implementing SpaceAPI.

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Note**: This project only accesses publicly available data that hackerspaces have chosen to share via SpaceAPI. No private information is collected or stored.
