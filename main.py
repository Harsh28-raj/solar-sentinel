import requests
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import random

# Custom Modules
from fetcher import fetch_nasa_solar_data
from processor import process_satellite_risk

app = FastAPI(title="HelioStar Professional Engine")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

master_satellites_list = []

def get_live_satellite_names():
    """Famous VIPs + Live Data + Generator (Ensures 1000 Unique Sats)"""
    vip_sats = [
        "ISS (ZARYA)", "HUBBLE SPACE TELESCOPE", "JAMES WEBB (JWST)", 
        "GPS NAVSTAR", "GOES-16 (NOAA)", "STARLINK-V2", "CHANDRAYAAN-3", 
        "ADITYA-L1", "SPUTNIK-1 (LEGACY)", "EXPLORER-1", "ARYABHATA"
    ]
    
    live_names = []
    try:
        url = "https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle"
        r = requests.get(url, timeout=3)
        if r.status_code == 200:
            lines = r.text.splitlines()
            live_names = [lines[i].strip() for i in range(0, 300, 3)]
    except:
        pass

    combined = vip_sats + live_names
    unique_names = []
    seen = set()
    for name in combined:
        if name not in seen:
            unique_names.append(name)
            seen.add(name)
            
    # Search Fix: Adding more variety prefixes
    prefixes = ["STARLINK", "IRIS", "COSMOS", "GENESIS", "OSIRIS", "METIS", "ONEWEB"]
    while len(unique_names) < 1000:
        f_name = f"{random.choice(prefixes)}-{random.randint(1000, 9999)}"
        if f_name not in seen:
            unique_names.append(f_name)
            seen.add(f_name)
            
    return unique_names[:1000]

def generate_full_report():
    global master_satellites_list
    solar_data = fetch_nasa_solar_data()
    names = get_live_satellite_names()
    
    temp = []
    for name in names:
        orbit = "GEO" if any(x in name.upper() for x in ["GOES", "INSAT", "GSAT", "METEOR"]) else "LEO"
        sat_data = process_satellite_risk(name, orbit, random.randint(1, 15), solar_data)
        temp.append(sat_data)
    
    master_satellites_list = temp
    return solar_data

@app.on_event("startup")
async def startup_event():
    generate_full_report()
    print(f"Engine Ready: {len(master_satellites_list)} Satellites Loaded")

@app.get("/api/helio-risk")
def get_risk_dashboard():
    """Strictly returns 4 Red, 3 Yellow, 3 Green for Dashboard"""
    solar_data = generate_full_report()
    
    # 1000 ki list mein se filtering
    high_risk = [s for s in master_satellites_list if s['risk_score'] > 75]
    med_risk = [s for s in master_satellites_list if 45 < s['risk_score'] <= 75]
    low_risk = [s for s in master_satellites_list if s['risk_score'] <= 45]
    
    # Strict 4-3-3 combination
    curated = high_risk[:4] + med_risk[:3] + low_risk[:3]
    
    # Safety: Agar list choti hai toh pehle 10 de do
    if len(curated) < 10:
        curated = master_satellites_list[:10]

    return {
        "metadata": solar_data["metadata"],
        "curated_top_10": curated,
        "all_satellites": master_satellites_list
    }

@app.get("/api/search")
def search_satellite(name: str):
    query = name.upper().strip()
    results = [s for s in master_satellites_list if query in s['name'].upper()]
    return results[:15]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
