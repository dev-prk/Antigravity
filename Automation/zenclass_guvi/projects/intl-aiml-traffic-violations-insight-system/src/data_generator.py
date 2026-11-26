"""Generates a realistic 43-column messy Traffic Violations dataset when the 839MB raw CSV is absent."""

from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

RAW_COLUMNS_43 = [
    "SeqID", "Date Of Stop", "Time Of Stop", "Agency", "SubAgency",
    "Description", "Location", "Latitude", "Longitude", "Accident",
    "Belts", "Personal Injury", "Property Damage", "Fatal", "Commercial License",
    "HAZMAT", "Commercial Vehicle", "Alcohol", "Work Zone", "Search Conducted",
    "Search Disposition", "Search Outcome", "Search Reason", "Search Reason For Stop",
    "Search Type", "Search Arrest Reason", "State", "VehicleType", "Year",
    "Make", "Model", "Color", "Violation Type", "Charge", "Article",
    "Contributed To Accident", "Race", "Gender", "Driver City", "Driver State",
    "DL State", "Arrest Type", "Geolocation",
]


def ensure_sample_raw_csv(output_path: Path, n_rows: int = 12000, seed: int = 42) -> Path:
    """Creates a realistic messy 43-column Montgomery County traffic violations CSV with real-world anomalies."""
    if output_path.exists():
        return output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)

    subagencies = [
        ("1st District, Rockville", 39.0840, -77.1528),
        ("2nd District, Bethesda", 38.9847, -77.0947),
        ("3rd District, Silver Spring", 38.9907, -77.0261),
        ("4th District, Wheaton", 39.0398, -77.0553),
        ("5th District, Germantown", 39.1732, -77.2717),
        ("6th District, Gaithersburg / Montgomery Village", 39.1434, -77.2014),
        ("Headquarters and Special Operations", 39.1085, -77.1960),
    ]
    corridors = [
        "I-270 AT MONTROSE RD", "GEORGIA AVE @ COLESVILLE RD", "ROCKVILLE PIKE @ HALPINE RD",
        "I-495 OUTER LOOP @ CONNECTICUT AVE", "VEIRS MILL RD @ RANDOLPH RD",
        "NEW HAMPSHIRE AVE @ LOCKWOOD DR", "FREDERICK RD @ SHADY GROVE RD",
        "WISCONSIN AVE @ EAST WEST HWY", "US 29 @ TECH RD", "CLOPPER RD @ GREAT SENECA HWY",
    ]
    violations = [
        ("EXCEEDING MAXIMUM SPEED: 74 MPH IN A POSTED 55 MPH ZONE", "21-801.1", "Citation"),
        ("DRIVER FAILURE TO OBEY PROPERLY PLACED TRAFFIC CONTROL DEVICE INSTRUCTIONS", "21-201(a1)", "Citation"),
        ("FAILURE TO STOP AT STOP SIGN", "21-707(a)", "Warning"),
        ("DRIVING VEHICLE WHILE UNDER THE INFLUENCE OF ALCOHOL", "21-902(a1)", "Citation"),
        ("DRIVER USING HANDS TO USE HANDHELD TELEPHONE WHILE MOTOR VEHICLE IS IN MOTION", "21-1124.2(d2)", "Citation"),
        ("OPERATING UNINSURED VEHICLE", "17-107", "Citation"),
        ("FAILURE TO DISPLAY REGISTRATION CARD UPON DEMAND BY POLICE OFFICER", "13-409(b)", "Warning"),
        ("DRIVER FAIL TO MAKE SURE ALL PASSENGERS UNDER 16 ARE SECURED BY SEAT BELT", "22-412.3(b)", "Citation"),
        ("NEGLIGENT DRIVING VEHICLE IN CARELESS AND IMPRUDENT MANNER ENDANGERING PROPERTY, LIFE AND PERSON", "21-901.1(b)", "Citation"),
        ("HEADLIGHTS/TAILLIGHTS INOPERATIVE", "22-201.1", "SERO"),
    ]
    makes_models = [
        ("TOYOTA", "CAMRY"), ("toyota", "COROLLA"), ("HONDA", "CIVIC"), ("Honda ", "ACCORD"),
        ("FORD", "F-150"), ("FORD", "EXPLORER"), ("NISSAN", "ALTIMA"), ("CHEVROLET", "MALIBU"),
        ("HYUNDAI", "ELANTRA"), ("BMW", "328I"), ("TESLA", "MODEL 3"), ("SUBARU", "OUTBACK"),
    ]
    vehicle_types = ["02 - Automobile", "05 - Light Duty Truck", "01 - Motorcycle", "06 - Heavy Duty Truck", "03 - Station Wagon"]
    colors = ["BLACK", "SILVER", "WHITE", "GRAY", "BLUE", "RED", "white ", "Gold"]
    races = ["WHITE", "BLACK", "HISPANIC", "ASIAN", "OTHER", "NATIVE AMERICAN"]
    genders = ["M", "F", "U"]
    cities = ["SILVER SPRING", "ROCKVILLE", "GAITHERSBURG", "GERMANTOWN", "BETHESDA", "WHEATON", "LAUREL", "WASHINGTON"]
    arrest_types = [
        "A - Marked Patrol", "B - Unmarked Patrol", "Q - Marked Laser",
        "R - Unmarked Laser", "S - License Plate Recognition", "G - Marked Moving Radar (Stationary)",
    ]

    # Create repeated SeqIDs (~12% multi-charge traffic stops)
    unique_stops = int(n_rows * 0.88)
    base_ids = [f"SEQ-{100000 + i:06d}" for i in range(unique_stops)]
    repeated_ids = rng.choice(base_ids, size=n_rows - unique_stops, replace=True).tolist()
    seq_ids = base_ids + repeated_ids
    rng.shuffle(seq_ids)

    # Hour distribution weighted toward morning/evening rush & late-night enforcement
    hour_probs = np.array([
        0.035, 0.030, 0.022, 0.015, 0.012, 0.018, 0.038, 0.065,
        0.078, 0.060, 0.048, 0.045, 0.044, 0.046, 0.052, 0.062,
        0.072, 0.075, 0.055, 0.040, 0.032, 0.025, 0.018, 0.013,
    ])
    hour_probs = hour_probs / hour_probs.sum()

    rows = []
    start_ts = pd.Timestamp("2023-01-01")
    for i in range(n_rows):
        sub_name, base_lat, base_lon = subagencies[int(rng.integers(0, len(subagencies)))]
        day_offset = int(rng.integers(0, 730))
        dt = start_ts + pd.Timedelta(days=day_offset)
        # Mix date formats intentionally to exercise cleaner
        date_str = dt.strftime("%m/%d/%Y") if i % 5 != 0 else dt.strftime("%Y-%m-%d")
        hr = int(rng.choice(np.arange(24), p=hour_probs))
        mn = int(rng.integers(0, 60))
        sc = int(rng.integers(0, 60))
        time_str = f"{hr:02d}:{mn:02d}:{sc:02d}"

        desc, charge, vtype = violations[int(rng.integers(0, len(violations)))]
        is_dui = "ALCOHOL" in desc
        lat = round(float(base_lat + rng.normal(0, 0.035)), 6)
        lon = round(float(base_lon + rng.normal(0, 0.035)), 6)
        geoloc = f"({lat}, {lon})"

        # Inject realistic coordinate anomalies (0.0 or missing Latitude recoverable from Geolocation)
        raw_lat: object = lat
        raw_lon: object = lon
        if i % 40 == 0:
            raw_lat, raw_lon = 0.0, 0.0  # Recoverable from Geolocation!
        elif i % 95 == 0:
            raw_lat, raw_lon, geoloc = 99.99, -200.0, ""  # Out-of-bounds invalid

        accident = "Yes" if rng.random() < (0.14 if is_dui else 0.045) else ("no" if i % 7 == 0 else "No")
        prop_dmg = "Yes" if (accident == "Yes" and rng.random() < 0.65) else "No"
        pers_inj = "Yes" if (accident == "Yes" and rng.random() < 0.28) else "No"
        fatal = "Yes" if (pers_inj == "Yes" and rng.random() < 0.03) else "No"
        belts = "Yes" if "SEAT BELT" in desc or rng.random() < 0.04 else "No"
        alcohol = "Yes" if is_dui or rng.random() < 0.025 else "No"
        search_cond = "Yes" if (is_dui or rng.random() < 0.06) else "No"

        make, model = makes_models[int(rng.integers(0, len(makes_models)))]
        yr = int(rng.integers(2004, 2026))
        if i % 60 == 0:
            yr = int(rng.choice([0, 1900, 2099, 9999]))  # Invalid vehicle years to sanitize

        rows.append({
            "SeqID": seq_ids[i],
            "Date Of Stop": date_str,
            "Time Of Stop": time_str,
            "Agency": "MCP",
            "SubAgency": sub_name,
            "Description": desc,
            "Location": corridors[int(rng.integers(0, len(corridors)))],
            "Latitude": raw_lat,
            "Longitude": raw_lon,
            "Accident": accident,
            "Belts": belts,
            "Personal Injury": pers_inj,
            "Property Damage": prop_dmg,
            "Fatal": fatal,
            "Commercial License": "Yes" if rng.random() < 0.05 else "No",
            "HAZMAT": "Yes" if rng.random() < 0.004 else "No",
            "Commercial Vehicle": "Yes" if rng.random() < 0.04 else "No",
            "Alcohol": alcohol,
            "Work Zone": "Yes" if rng.random() < 0.02 else "No",
            "Search Conducted": search_cond,
            "Search Disposition": rng.choice(["Nothing", "Contraband Only", "Property Only", "Contraband and Property"]) if search_cond == "Yes" else np.nan,
            "Search Outcome": rng.choice(["Arrest", "Citation", "Warning"]) if search_cond == "Yes" else (rng.choice(["Citation", "Warning", "SERO"])),
            "Search Reason": rng.choice(["Probable Cause", "Incident to Arrest", "Consensual"]) if search_cond == "Yes" else np.nan,
            "Search Reason For Stop": charge,
            "Search Type": rng.choice(["Both", "Property", "Person"]) if search_cond == "Yes" else np.nan,
            "Search Arrest Reason": rng.choice(["DUI", "Controlled Substance", "Driving Without License"]) if search_cond == "Yes" else np.nan,
            "State": rng.choice(["MD", "MD", "MD", "VA", "DC", "PA"]),
            "VehicleType": vehicle_types[int(rng.integers(0, len(vehicle_types)))],
            "Year": yr,
            "Make": make,
            "Model": model,
            "Color": colors[int(rng.integers(0, len(colors)))],
            "Violation Type": vtype,
            "Charge": charge,
            "Article": "Transportation Article" if vtype != "SERO" else np.nan,
            "Contributed To Accident": accident,
            "Race": races[int(rng.integers(0, len(races)))],
            "Gender": rng.choice(genders, p=[0.62, 0.36, 0.02]),
            "Driver City": cities[int(rng.integers(0, len(cities)))],
            "Driver State": rng.choice(["MD", "MD", "VA", "DC"]),
            "DL State": rng.choice(["MD", "MD", "VA", "DC", "PA"]),
            "Arrest Type": arrest_types[int(rng.integers(0, len(arrest_types)))],
            "Geolocation": geoloc,
        })

    df = pd.DataFrame(rows, columns=RAW_COLUMNS_43)
    df.to_csv(output_path, index=False)
    return output_path
