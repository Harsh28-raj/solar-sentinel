def get_flare_details(flux):
    """
    X-Ray Flux value ko standard NASA Flare Class mein convert karta hai
    aur points assign karta hai (Max points: 21)
    """
    if flux >= 1e-4: 
        return {"class": f"X{round(flux/1e-4, 1)}", "pts": 21}
    elif flux >= 1e-5: 
        return {"class": f"M{round(flux/1e-5, 1)}", "pts": 15}
    elif flux >= 1e-6:
        return {"class": f"C{round(flux/1e-6, 1)}", "pts": 10}
    else:
        # Jab suraj ekdum shant ho (A ya B class)
        return {"class": "Quiet/Baseline", "pts": 5}

def calculate_sat_risk(x_flux, p_flux, orbit, age):
    """
    Tere Formula Weights:
    Orbit (W1): 35 | Age (W2): 28 | Flux (W3): 21 | Angle (W4): 16
    Additional: Proton Storm Penalty (10 pts)
    """
    flare = get_flare_details(x_flux)
    
    # 1. Orbit Weight (W1) - GEO satellites are more exposed
    w_orbit = 35 if orbit == "GEO" else 15
    
    # 2. Age Weight (W2) - 10 saal se purani satellites are fragile
    w_age = 28 if age > 10 else 10
    
    # 3. Flux/Flare Weight (W3) - Based on NASA class
    w_flux = flare['pts']
    
    # 4. Exposure Angle (W4) - Constant for direct exposure
    w_angle = 16 
    
    # 5. Radiation Storm Impact (Proton Flux)
    # Agar Proton Flux threshold (>10 pfu) se upar hai toh extra risk
    p_penalty = 0
    if p_flux > 10:
        p_penalty = 10  # Solar Radiation Storm detected
    
    # Final Score Calculation (Capped at 100)
    total_score = min(w_orbit + w_age + w_flux + w_angle + p_penalty, 100)
    
    # Severity Levels for UI Mapping
    if total_score > 75:
        status = "CRITICAL"
        color = "#FF4D4D"  # Neon Red
        action = "Immediate Safe Mode: Shut down non-essential systems"
    elif total_score > 45:
        status = "WARNING"
        color = "#FFD700"  # Golden Yellow
        action = "Monitor for single-event upsets (Bit-flips)"
    else:
        status = "SAFE"
        color = "#00FA9A"  # Spring Green
        action = "Nominal Operations: All systems healthy"
        
    return total_score, status, color, action