import requests
from skyfield.api import load, EarthSatellite

# 1. LIVE SOLAR X-RAY FLUX (Flares ke liye)
def get_live_flux():
    url = "https://services.swpc.noaa.gov/json/goes/primary/xrays-7-day.json"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        latest = [e for e in data if e['energy'] == '0.1-0.8nm'][-1]
        return latest['flux']
    except Exception:
        return 1.0e-7  # Fallback

# 2. LIVE PROTON FLUX (Radiation Storms ke liye)
def get_proton_flux():
    url = "https://services.swpc.noaa.gov/json/goes/primary/proton-flux-5-minute.json"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        # >10 MeV energy band ka latest data uthana
        latest = [e for e in data if e['energy'] == '>10 MeV'][-1]
        return latest['flux']
    except Exception:
        return 0.1  # Fallback

# 3. LIVE SATELLITE COORDINATES (TLE to Lat/Lon)
def get_sat_coords(name, line1, line2):
    try:
        ts = load.timescale()
        t = ts.now()
        satellite = EarthSatellite(line1, line2, name, ts)
        geocentric = satellite.at(t)
        subpoint = geocentric.subpoint()
        return {
            "lat": round(subpoint.latitude.degrees, 4),
            "lon": round(subpoint.longitude.degrees, 4)
        }
    except Exception:
        return {"lat": 0.0, "lon": 0.0}

# 4. TLE DATABASE (10 Major Satellites for UI)
def get_tle_data():
    return {
        "ISS (ZARYA)": [
            "1 25544U 98067A   24111.51345448  .00016717  00000-0  30142-3 0  9998",
            "2 25544  51.6393  63.5352 0005011 106.8457  43.2085 15.49474706450257"
        ],
        "INSAT-3DR": [
            "1 41752U 16054A   24111.21453211 -.00000123  00000-0  00000-0 0  9991",
            "2 41752   0.0452  82.1245 0001241 210.1245  12.4512  1.00271452 3451"
        ],
        "HUBBLE": [
            "1 20580U 90037B   24111.45123412  .00001234  00000-0  56789-4 0  9994",
            "2 20580  28.4690 154.2314 0002841  89.1245 271.4512 15.084512341234"
        ],
        "GSAT-11": [
            "1 43816U 18099A   24111.12345678  .00000012  00000-0  00000-0 0  9992",
            "2 43816   0.0123  95.4321 0001234 180.1234  10.1234  1.00273456 1234"
        ],
        "STARLINK-1204": [
            "1 45359U 20025AU  24111.55432109  .00012345  00000-0  12345-3 0  9993",
            "2 45359  53.0543 210.4321 0001234  45.1234 315.4321 15.05432109 1234"
        ],
        "GPS-III SV01": [
            "1 43873U 18109A   24111.65432100  .00000045  00000-0  00000-0 0  9995",
            "2 43873  55.1234  45.1234 0001234 120.4321 240.1234  2.00567890 1234"
        ],
        "GOES-18": [
            "1 51850U 22021A   24111.34567812 -.00000112  00000-0  00000-0 0  9996",
            "2 51850   0.0234 105.1234 0001234 190.1234  15.1234  1.00271122 1234"
        ],
        "METEOSAT-11": [
            "1 40732U 15034A   24111.23456789  .00000022  00000-0  00000-0 0  9997",
            "2 40732   0.0345  75.4321 0001234 200.4321  20.4321  1.00275566 1234"
        ],
        "AMAZON KUIPER-1": [
            "1 58000U 23150A   24111.43210987  .00023456  00000-0  45678-3 0  9998",
            "2 58000  51.4321 310.1234 0001234  90.4321 270.1234 15.12345678 1234"
        ],
        "ARYABHATA-NEXT": [
            "1 99999U 24001A   24111.11111111  .00011111  00000-0  11111-3 0  9999",
            "2 99999  45.1111  11.1111 0001111  11.1111  11.1111 15.11111111    1"
        ]
    }