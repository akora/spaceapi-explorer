# Hackerspace Guide: Getting Listed in SpaceAPI

A quick tutorial for hackerspace operators on how to get your space listed in the SpaceAPI directory.

## 🎯 What is SpaceAPI?

SpaceAPI is a standardized way for hackerspaces to share information like:

- **Open/closed status** - Is your space currently open?
- **Location** - Address and GPS coordinates
- **Contact info** - Email, IRC, social media
- **Events** - Recent activities
- **Sensors** - Temperature, humidity, door sensors

## 📋 Requirements

### **Technical Requirements:**

- ✅ **Web server** - Can host a simple JSON file
- ✅ **HTTP endpoint** - Accessible via HTTPS (recommended)
- ✅ **JSON format** - Follow SpaceAPI schema
- ✅ **Real-time updates** - Status changes should be current

### **Content Requirements:**

- ✅ **Space name** - Your hackerspace's name
- ✅ **Location data** - Address or coordinates
- ✅ **API version** - Specify which SpaceAPI version you use
- ✅ **Contact method** - At least one way to reach you

## 🚀 Quick Setup (5 Minutes)

### **Step 1: Create Your SpaceAPI File**

Create a file called `spaceapi.json` on your web server:

```json
{
  "api": "0.13",
  "space": "My Hackerspace",
  "url": "https://myhackerspace.org",
  "location": {
    "address": "123 Maker Street, City, Country",
    "lat": 52.5200,
    "lon": 13.4050
  },
  "contact": {
    "email": "info@myhackerspace.org",
    "twitter": "@myhackerspace"
  },
  "state": {
    "open": false,
    "lastchange": 1640995200,
    "icon": {
      "open": "https://myhackerspace.org/img/open.png",
      "closed": "https://myhackerspace.org/img/closed.png"
    }
  }
}
```

### **Step 2: Make It Accessible**

Upload to your web server so it's available at:

```text
https://YOUR-DOMAIN.COM/spaceapi.json
```

**Replace `YOUR-DOMAIN.COM` with your actual domain name**, for example:

- `https://milklab.ie/spaceapi.json` (Irish hackerspace)
- `https://ccc.de/spaceapi.json` (German hackerspace)
- `https://tokyomakerspace.jp/spaceapi.json` (Japanese hackerspace)
- `https://makerspace.local/spaceapi.json` (Local development)

Test it: `curl https://YOUR-DOMAIN.COM/spaceapi.json`

### **Step 3: Submit to Directory**

1. **Go to**: [SpaceAPI Directory](https://directory.spaceapi.io/)
2. **Find submission info** - Usually in GitHub issues or wiki
3. **Submit your endpoint** - Provide your space name and URL
4. **Wait for review** - Maintainers will validate your endpoint

## 📖 Advanced Features

### **Dynamic Status (Recommended)**

Instead of manually updating `spaceapi.json`, make it dynamic:

```python
# Example with Flask (Python)
from flask import Flask, jsonify
import json
import time

app = Flask(__name__)

@app.route('/spaceapi.json')
def spaceapi():
    # Check if space is open (your logic here)
    is_open = check_door_sensor()
    
    return jsonify({
        "api": "0.13",
        "space": "My Hackerspace",
        "location": {"address": "123 Maker Street"},
        "state": {
            "open": is_open,
            "lastchange": int(time.time())
        }
    })
```

### **Add Sensors**

```json
{
  "sensors": {
    "temperature": [
      {
        "name": "Room Temperature",
        "unit": "°C",
        "value": 22.5
      }
    ],
    "door_locked": [
      {
        "name": "Front Door",
        "value": false
      }
    ]
  }
}
```

### **Add Events**

```json
{
  "events": [
    {
      "name": "Weekly Meeting",
      "type": "meeting",
      "timestamp": 1640995200,
      "extra": {
        "description": "Weekly members meeting"
      }
    }
  ]
}
```

## 🔧 Common Implementations

### **Static JSON (Easiest)**

- **Pros**: Simple, no programming required
- **Cons**: Manual updates, not real-time
- **Best for**: Small spaces with basic needs

### **Dynamic Endpoint (Recommended)**

- **Pros**: Real-time data, automated updates
- **Cons**: Requires programming
- **Best for**: Most spaces with technical members

### **Existing Solutions**

**Home Automation Integration:**

- **Home Assistant** - [Has SpaceAPI component](https://www.home-assistant.io/integrations/spaceapi/)
- **OpenHAB** - [Can generate SpaceAPI via REST API](https://www.openhab.org/docs/configuration/restdocs.html)
- **Custom scripts** - Hook into your door system

## ✅ Validation Checklist

Before submitting, verify your endpoint:

### **Basic Tests:**

```bash
# Should return 200 OK
curl -I https://myhackerspace.org/spaceapi.json

# Should be valid JSON
curl https://myhackerspace.org/spaceapi.json | jq .

# Should have required fields
curl https://myhackerspace.org/spaceapi.json | jq '.space, .location, .state'
```

### **Required Fields:**

- ✅ `api` or `api_compatibility` - Version info
- ✅ `space` - Space name
- ✅ `location` - Address or coordinates
- ✅ `state.open` - Current status (can be null)

### **Recommended Fields:**

- ✅ `url` - Your website
- ✅ `contact` - How to reach you
- ✅ `state.lastchange` - Last status change timestamp

## 🚨 Common Mistakes to Avoid

### **Don't:**

- ❌ Use HTTP only (use HTTPS)
- ❌ Return HTML instead of JSON
- ❌ Forget required fields
- ❌ Use invalid timestamps
- ❌ Hardcode wrong coordinates

### **Do:**

- ✅ Test your endpoint regularly
- ✅ Keep status updates current
- ✅ Use proper JSON syntax
- ✅ Include contact information
- ✅ Monitor for errors

## 📞 Getting Help

### **Community Resources:**

- **IRC**: #spaceapi on Libera.chat
- **GitHub**: [SpaceAPI organization](https://github.com/SpaceApi)
- **Documentation**: [spaceapi.io](https://spaceapi.io/)

### **Validation Tools:**

- **JSON Lint**: [jsonlint.com](https://jsonlint.com/)
- **SpaceAPI Validator**: Online tools available
- **Community Review**: Ask in IRC for feedback

## 🎉 Success

Once listed:

- 🌍 **Global visibility** - Your space appears on maps and directories
- 📊 **Data analysis** - Contribute to hackerspace research
- 🤝 **Community** - Join the SpaceAPI ecosystem
- 🔄 **Real-time status** - Help others know when you're open

## 📈 Next Steps

After getting listed:

1. **Add sensors** - Temperature, door status, etc.
2. **Integrate events** - Meeting schedules, activities
3. **Join community** - Participate in SpaceAPI development
4. **Help others** - Share your implementation experience

---

## **Welcome to the SpaceAPI community! 🚀**

*This guide covers the essentials. For complete schema documentation, visit [spaceapi.io/docs](https://spaceapi.io/docs).*
