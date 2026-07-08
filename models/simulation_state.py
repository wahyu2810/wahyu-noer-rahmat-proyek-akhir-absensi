import datetime
import urllib.request
import json

# Global simulation parameters
use_simulation = False
simulated_hour = 9
simulated_minute = 30
simulated_second = 0

simulated_lat = -6.490333  # Defaults to Kampus B
simulated_lon = 106.731667

# Real location cache
_real_lat = None
_real_lon = None

def get_real_location():
    global _real_lat, _real_lon
    if _real_lat is not None and _real_lon is not None:
        return _real_lat, _real_lon
    try:
        # Fetch public IP geolocation
        req = urllib.request.Request(
            "http://ip-api.com/json/",
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=3) as response:
            data = json.loads(response.read().decode())
            if data.get("status") == "success":
                _real_lat = float(data.get("lat"))
                _real_lon = float(data.get("lon"))
                return _real_lat, _real_lon
    except Exception:
        pass
    # Fallback to Campus B coordinates if geolocation fails
    return -6.490333, 106.731667

def get_current_location():
    if use_simulation:
        return simulated_lat, simulated_lon
    return get_real_location()

def get_current_time():
    if use_simulation:
        now = datetime.datetime.now()
        try:
            return now.replace(hour=simulated_hour, minute=simulated_minute, second=simulated_second)
        except ValueError:
            return now
    return datetime.datetime.now()
