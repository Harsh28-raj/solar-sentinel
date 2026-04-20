import random
from datetime import datetime

def process_satellite_risk(name, orbit, age, solar_data):
    """
    Risk Score + Coordinates + Short Recommendations.
    Ranges are adjusted to ensure variety (Red/Yellow/Green).
    """
    try:
        # Variety Logic: Ranges badha di hain taaki har category mile
        if orbit == "GEO":
            # GEO satellites usually higher risk
            base_risk = random.randint(65, 95) 
        else:
            # LEO covers the full spectrum
            base_risk = random.randint(10, 85)

        # Solar flux impact from NASA data
        flux = solar_data.get("metadata", {}).get("x_ray_flux", 1e-7)
        solar_factor = 10 if flux > 1e-6 else 0
        
        total_risk = min(98, max(5, base_risk + solar_factor + (age * 0.4)))

        # UI Color and Status Assignment
        if total_risk > 75:
            color, status = "#FF4D4D", "CRITICAL"
            rec = "Shielding: ACTIVE | Mode: SAFE"
        elif total_risk > 45:
            color, status = "#FFD700", "WARNING"
            rec = "Link: REDUNDANT | Status: MONITOR"
        else:
            color, status = "#00FA9A", "NOMINAL"
            rec = "Systems: OPTIMAL | Ops: NORMAL"

        return {
            "name": name,
            "orbit": orbit,
            "lat": round(random.uniform(-90, 90), 4),
            "lng": round(random.uniform(-180, 180), 4),
            "alt": 35786 if orbit == "GEO" else random.randint(400, 1200),
            "age": age,
            "risk_score": round(total_risk, 2),
            "ui_color": color,
            "status": status,
            "recommendation": rec,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        return {"name": name, "risk_score": 50, "status": "ERROR", "recommendation": "Check Engine"}
