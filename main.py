from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import fetcher
import processor

app = FastAPI(
    title="HelioScar Satellite Risk API",
    description="Live Satellite Risk Monitoring based on Solar Flux and TLE data",
    version="1.0.0"
)

# Frontend Integration ke liye CORS Settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Sabhi origins allow hain (Testing/Hackathon ke liye best)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "status": "Online",
        "system": "HelioScar Mod-1",
        "documentation": "/docs"
    }

@app.get("/api/helio-risk")
def helio_risk_api():
    # 1. Fetch Live Data from NASA/NOAA (via fetcher.py)
    x_flux = fetcher.get_live_flux()
    p_flux = fetcher.get_proton_flux()
    tle_db = fetcher.get_tle_data()
    
    # Flare Details nikalna (A, B, C, M, X Class)
    flare_info = processor.get_flare_details(x_flux)
    
    # 2. Satellite Inventory (10 Satellites for Dashboard)
    sat_list = [
        {"name": "ISS (ZARYA)", "orbit": "LEO", "age": 26},
        {"name": "INSAT-3DR", "orbit": "GEO", "age": 8},
        {"name": "HUBBLE", "orbit": "LEO", "age": 34},
        {"name": "GSAT-11", "orbit": "GEO", "age": 6},
        {"name": "STARLINK-1204", "orbit": "LEO", "age": 2},
        {"name": "GPS-III SV01", "orbit": "MEO", "age": 5},
        {"name": "GOES-18", "orbit": "GEO", "age": 2},
        {"name": "METEOSAT-11", "orbit": "GEO", "age": 9},
        {"name": "AMAZON KUIPER-1", "orbit": "LEO", "age": 1},
        {"name": "ARYABHATA-NEXT", "orbit": "LEO", "age": 1}
    ]
    
    processed_sats = []
    
    # 3. Har satellite ke liye Risk aur Location calculate karna
    for sat in sat_list:
        # A. TLE data se Latitude/Longitude nikalna
        tle = tle_db.get(sat['name'], ["", ""])
        coords = fetcher.get_sat_coords(sat['name'], tle[0], tle[1])
        
        # B. Risk Formula apply karna (Logic from processor.py)
        score, status, color, action = processor.calculate_sat_risk(
            x_flux, p_flux, sat['orbit'], sat['age']
        )
        
        # C. Satellite ka final data object banana
        processed_sats.append({
            "name": sat['name'],
            "orbit": sat['orbit'],
            "age": f"{sat['age']} yrs",
            "risk_score": score,
            "status": status,
            "ui_color": color,
            "recommendation": action,
            "coordinates": {
                "lat": coords['lat'],
                "lon": coords['lon']
            }
        })

    # 4. Final Unified Response for Frontend
    return {
        "metadata": {
            "timestamp": "Live",
            "flare_class": flare_info['class'],
            "x_ray_flux": x_flux,
            "proton_flux": p_flux,
            "global_alert": "Nominal" if x_flux < 1e-5 else "Solar Flare Warning"
        },
        "satellites": processed_sats
    }

# Command to Run: python -m uvicorn main:app --reload