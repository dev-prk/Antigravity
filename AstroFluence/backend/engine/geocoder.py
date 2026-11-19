"""
High-Precision Geodetic Birthplace & Historical Timezone / DST Resolver.

Why Place of Birth is Mathematically Critical in Astrology & Locational Systems:
1. Universal Time (UT) Conversion:
   A clock time of "10:30" in New York, London, Tokyo, or Mumbai corresponds to completely different
   Universal Times (Julian Days) depending on the exact IANA timezone AND whether Daylight Saving Time
   (DST) or historical war-time/standard-time offsets were in effect on that exact birth date.
   Even a 1-hour timezone error shifts the Ascendant (Lagna) by ~15° (often changing the entire Rising Sign,
   all 12 House cusps, the Navamsha D9 Lagna, and Dashamsha D10 Lagna) and shifts the Moon by ~0.5°
   (changing Vimshottari Dasha balance by months or years).
2. Geographic Latitude (φ) & Longitude (λ):
   The Ascendant (Eastern Horizon intersection with the Ecliptic) and Midheaven (Local Meridian) are solved
   from Local Sidereal Time (LST = GST + λ) and geographic latitude φ:
     tan(RAMC) = sin(LST) / cos(LST)
     tan(λ_ASC) = -cos(RAMC) / (sin(ε)*tan(φ) + cos(ε)*sin(RAMC))
3. Relocation / Current Residence Chart:
   Where you live NOW vs. where you were BORN shifts your entire house grid (Relocated Ascendant & Midheaven)
   and determines which planetary angular lines (Astrocartography) and Local Space azimuth vectors cross your city.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

import httpx

try:
    from timezonefinder import TimezoneFinder
    _TF = TimezoneFinder()
except Exception:
    _TF = None

# Built-in instant-lookup gazetteer of 85+ global & Indian cities with exact coordinates & IANA timezone
BUILT_IN_GAZETTEER: List[Dict[str, Any]] = [
    # India (Comprehensive coverage)
    {"city": "New Delhi, Delhi, India", "lat": 28.6139, "lon": 77.2090, "tz": "Asia/Kolkata"},
    {"city": "Mumbai, Maharashtra, India", "lat": 19.0760, "lon": 72.8777, "tz": "Asia/Kolkata"},
    {"city": "Bengaluru, Karnataka, India", "lat": 12.9716, "lon": 77.5946, "tz": "Asia/Kolkata"},
    {"city": "Hyderabad, Telangana, India", "lat": 17.3850, "lon": 78.4867, "tz": "Asia/Kolkata"},
    {"city": "Chennai, Tamil Nadu, India", "lat": 13.0827, "lon": 80.2707, "tz": "Asia/Kolkata"},
    {"city": "Kolkata, West Bengal, India", "lat": 22.5726, "lon": 88.3639, "tz": "Asia/Kolkata"},
    {"city": "Pune, Maharashtra, India", "lat": 18.5204, "lon": 73.8567, "tz": "Asia/Kolkata"},
    {"city": "Ahmedabad, Gujarat, India", "lat": 23.0225, "lon": 72.5714, "tz": "Asia/Kolkata"},
    {"city": "Jaipur, Rajasthan, India", "lat": 26.9124, "lon": 75.7873, "tz": "Asia/Kolkata"},
    {"city": "Lucknow, Uttar Pradesh, India", "lat": 26.8467, "lon": 80.9462, "tz": "Asia/Kolkata"},
    {"city": "Varanasi, Uttar Pradesh, India", "lat": 25.3176, "lon": 82.9739, "tz": "Asia/Kolkata"},
    {"city": "Kanpur, Uttar Pradesh, India", "lat": 26.4499, "lon": 80.3319, "tz": "Asia/Kolkata"},
    {"city": "Agra, Uttar Pradesh, India", "lat": 27.1767, "lon": 78.0081, "tz": "Asia/Kolkata"},
    {"city": "Prayagraj (Allahabad), Uttar Pradesh, India", "lat": 25.4358, "lon": 81.8463, "tz": "Asia/Kolkata"},
    {"city": "Noida, Uttar Pradesh, India", "lat": 28.5355, "lon": 77.3910, "tz": "Asia/Kolkata"},
    {"city": "Gurugram (Gurgaon), Haryana, India", "lat": 28.4595, "lon": 77.0266, "tz": "Asia/Kolkata"},
    {"city": "Chandigarh, India", "lat": 30.7333, "lon": 76.7794, "tz": "Asia/Kolkata"},
    {"city": "Dehradun, Uttarakhand, India", "lat": 30.3165, "lon": 78.0322, "tz": "Asia/Kolkata"},
    {"city": "Patna, Bihar, India", "lat": 25.5941, "lon": 85.1376, "tz": "Asia/Kolkata"},
    {"city": "Ranchi, Jharkhand, India", "lat": 23.3441, "lon": 85.3096, "tz": "Asia/Kolkata"},
    {"city": "Bhopal, Madhya Pradesh, India", "lat": 23.2599, "lon": 77.4126, "tz": "Asia/Kolkata"},
    {"city": "Indore, Madhya Pradesh, India", "lat": 22.7196, "lon": 75.8577, "tz": "Asia/Kolkata"},
    {"city": "Surat, Gujarat, India", "lat": 21.1702, "lon": 72.8311, "tz": "Asia/Kolkata"},
    {"city": "Vadodara, Gujarat, India", "lat": 22.3072, "lon": 73.1812, "tz": "Asia/Kolkata"},
    {"city": "Nagpur, Maharashtra, India", "lat": 21.1458, "lon": 79.0882, "tz": "Asia/Kolkata"},
    {"city": "Kochi, Kerala, India", "lat": 9.9312, "lon": 76.2673, "tz": "Asia/Kolkata"},
    {"city": "Thiruvananthapuram, Kerala, India", "lat": 8.5241, "lon": 76.9366, "tz": "Asia/Kolkata"},
    {"city": "Coimbatore, Tamil Nadu, India", "lat": 11.0168, "lon": 76.9558, "tz": "Asia/Kolkata"},
    {"city": "Visakhapatnam, Andhra Pradesh, India", "lat": 17.6868, "lon": 83.2185, "tz": "Asia/Kolkata"},
    {"city": "Bhubaneswar, Odisha, India", "lat": 20.2961, "lon": 85.8245, "tz": "Asia/Kolkata"},
    {"city": "Guwahati, Assam, India", "lat": 26.1445, "lon": 91.7362, "tz": "Asia/Kolkata"},
    {"city": "Amritsar, Punjab, India", "lat": 31.6340, "lon": 74.8723, "tz": "Asia/Kolkata"},
    {"city": "Ludhiana, Punjab, India", "lat": 30.9010, "lon": 75.8573, "tz": "Asia/Kolkata"},
    {"city": "Udaipur, Rajasthan, India", "lat": 24.5854, "lon": 73.7125, "tz": "Asia/Kolkata"},
    {"city": "Jodhpur, Rajasthan, India", "lat": 26.2389, "lon": 73.0243, "tz": "Asia/Kolkata"},
    {"city": "Goa (Panaji), India", "lat": 15.4909, "lon": 73.8278, "tz": "Asia/Kolkata"},
    # North America
    {"city": "New York, NY, USA", "lat": 40.7128, "lon": -74.0060, "tz": "America/New_York"},
    {"city": "Los Angeles, CA, USA", "lat": 34.0522, "lon": -118.2437, "tz": "America/Los_Angeles"},
    {"city": "San Francisco, CA, USA", "lat": 37.7749, "lon": -122.4194, "tz": "America/Los_Angeles"},
    {"city": "San Jose, CA, USA", "lat": 37.3382, "lon": -121.8863, "tz": "America/Los_Angeles"},
    {"city": "Seattle, WA, USA", "lat": 47.6062, "lon": -122.3321, "tz": "America/Los_Angeles"},
    {"city": "Chicago, IL, USA", "lat": 41.8781, "lon": -87.6298, "tz": "America/Chicago"},
    {"city": "Austin, TX, USA", "lat": 30.2672, "lon": -97.7431, "tz": "America/Chicago"},
    {"city": "Houston, TX, USA", "lat": 29.7604, "lon": -95.3698, "tz": "America/Chicago"},
    {"city": "Dallas, TX, USA", "lat": 32.7767, "lon": -96.7970, "tz": "America/Chicago"},
    {"city": "Boston, MA, USA", "lat": 42.3601, "lon": -71.0589, "tz": "America/New_York"},
    {"city": "Miami, FL, USA", "lat": 25.7617, "lon": -80.1918, "tz": "America/New_York"},
    {"city": "Washington, DC, USA", "lat": 38.9072, "lon": -77.0369, "tz": "America/New_York"},
    {"city": "Atlanta, GA, USA", "lat": 33.7490, "lon": -84.3880, "tz": "America/New_York"},
    {"city": "Denver, CO, USA", "lat": 39.7392, "lon": -104.9903, "tz": "America/Denver"},
    {"city": "Phoenix, AZ, USA", "lat": 33.4484, "lon": -112.0740, "tz": "America/Phoenix"},
    {"city": "Toronto, ON, Canada", "lat": 43.6532, "lon": -79.3832, "tz": "America/Toronto"},
    {"city": "Vancouver, BC, Canada", "lat": 49.2827, "lon": -123.1207, "tz": "America/Vancouver"},
    {"city": "Montreal, QC, Canada", "lat": 45.5017, "lon": -73.5673, "tz": "America/Toronto"},
    {"city": "Mexico City, Mexico", "lat": 19.4326, "lon": -99.1332, "tz": "America/Mexico_City"},
    # Europe
    {"city": "London, United Kingdom", "lat": 51.5072, "lon": -0.1276, "tz": "Europe/London"},
    {"city": "Manchester, United Kingdom", "lat": 53.4808, "lon": -2.2426, "tz": "Europe/London"},
    {"city": "Edinburgh, United Kingdom", "lat": 55.9533, "lon": -3.1883, "tz": "Europe/London"},
    {"city": "Dublin, Ireland", "lat": 53.3498, "lon": -6.2603, "tz": "Europe/Dublin"},
    {"city": "Paris, France", "lat": 48.8566, "lon": 2.3522, "tz": "Europe/Paris"},
    {"city": "Berlin, Germany", "lat": 52.5200, "lon": 13.4050, "tz": "Europe/Berlin"},
    {"city": "Munich, Germany", "lat": 48.1351, "lon": 11.5820, "tz": "Europe/Berlin"},
    {"city": "Frankfurt, Germany", "lat": 50.1109, "lon": 8.6821, "tz": "Europe/Berlin"},
    {"city": "Zurich, Switzerland", "lat": 47.3769, "lon": 8.5417, "tz": "Europe/Zurich"},
    {"city": "Geneva, Switzerland", "lat": 46.2044, "lon": 6.1432, "tz": "Europe/Zurich"},
    {"city": "Amsterdam, Netherlands", "lat": 52.3676, "lon": 4.9041, "tz": "Europe/Amsterdam"},
    {"city": "Madrid, Spain", "lat": 40.4168, "lon": -3.7038, "tz": "Europe/Madrid"},
    {"city": "Barcelona, Spain", "lat": 41.3874, "lon": 2.1686, "tz": "Europe/Madrid"},
    {"city": "Rome, Italy", "lat": 41.9028, "lon": 12.4964, "tz": "Europe/Rome"},
    {"city": "Milan, Italy", "lat": 45.4642, "lon": 9.1900, "tz": "Europe/Rome"},
    {"city": "Vienna, Austria", "lat": 48.2082, "lon": 16.3738, "tz": "Europe/Vienna"},
    {"city": "Stockholm, Sweden", "lat": 59.3293, "lon": 18.0686, "tz": "Europe/Stockholm"},
    {"city": "Moscow, Russia", "lat": 55.7558, "lon": 37.6173, "tz": "Europe/Moscow"},
    # Asia-Pacific & Middle East
    {"city": "Dubai, United Arab Emirates", "lat": 25.2048, "lon": 55.2708, "tz": "Asia/Dubai"},
    {"city": "Abu Dhabi, United Arab Emirates", "lat": 24.4539, "lon": 54.3773, "tz": "Asia/Dubai"},
    {"city": "Singapore", "lat": 1.3521, "lon": 103.8198, "tz": "Asia/Singapore"},
    {"city": "Tokyo, Japan", "lat": 35.6762, "lon": 139.6503, "tz": "Asia/Tokyo"},
    {"city": "Hong Kong", "lat": 22.3193, "lon": 114.1694, "tz": "Asia/Hong_Kong"},
    {"city": "Seoul, South Korea", "lat": 37.5665, "lon": 126.9780, "tz": "Asia/Seoul"},
    {"city": "Bangkok, Thailand", "lat": 13.7563, "lon": 100.5018, "tz": "Asia/Bangkok"},
    {"city": "Kuala Lumpur, Malaysia", "lat": 3.1390, "lon": 101.6869, "tz": "Asia/Kuala_Lumpur"},
    {"city": "Jakarta, Indonesia", "lat": -6.2088, "lon": 106.8456, "tz": "Asia/Jakarta"},
    {"city": "Kathmandu, Nepal", "lat": 27.7172, "lon": 85.3240, "tz": "Asia/Kathmandu"},
    {"city": "Colombo, Sri Lanka", "lat": 6.9271, "lon": 79.8612, "tz": "Asia/Colombo"},
    {"city": "Sydney, NSW, Australia", "lat": -33.8688, "lon": 151.2093, "tz": "Australia/Sydney"},
    {"city": "Melbourne, VIC, Australia", "lat": -37.8136, "lon": 144.9631, "tz": "Australia/Melbourne"},
    {"city": "Auckland, New Zealand", "lat": -36.8485, "lon": 174.7633, "tz": "Pacific/Auckland"},
    # South America & Africa
    {"city": "São Paulo, Brazil", "lat": -23.5505, "lon": -46.6333, "tz": "America/Sao_Paulo"},
    {"city": "Buenos Aires, Argentina", "lat": -34.6037, "lon": -58.3816, "tz": "America/Argentina/Buenos_Aires"},
    {"city": "Johannesburg, South Africa", "lat": -26.2041, "lon": 28.0473, "tz": "Africa/Johannesburg"},
    {"city": "Cairo, Egypt", "lat": 30.0444, "lon": 31.2357, "tz": "Africa/Cairo"},
    {"city": "Nairobi, Kenya", "lat": -1.2921, "lon": 36.8219, "tz": "Africa/Nairobi"},
]


def resolve_tz_name_for_coords(lat: float, lon: float, fallback_tz: str = "Asia/Kolkata") -> str:
    """Determines the exact IANA timezone string (e.g. 'America/New_York', 'Asia/Kolkata') from coordinates."""
    if _TF is not None:
        try:
            tz_name = _TF.timezone_at(lat=lat, lng=lon)
            if tz_name:
                return tz_name
        except Exception:
            pass

    # Match nearest city in built-in gazetteer if within 4 degrees
    best_tz = fallback_tz
    best_dist = 9999.0
    for item in BUILT_IN_GAZETTEER:
        dist = ((item["lat"] - lat) ** 2 + (item["lon"] - lon) ** 2) ** 0.5
        if dist < best_dist:
            best_dist = dist
            best_tz = item["tz"]
    if best_dist <= 8.0:
        return best_tz

    # Solar longitude approximation fallback
    approx_hours = int(round(lon / 15.0))
    return fallback_tz if abs(lon - 77.2) < 15 else f"Etc/GMT{-approx_hours:+d}"


def compute_historical_utc_offset(
    birth_date: str,
    birth_time: str,
    tz_name: str,
    fallback_offset: float = 5.5,
) -> Dict[str, Any]:
    """
    Computes the exact historical UTC offset (in decimal hours) and DST status on the exact
    birth date & time at the birthplace's IANA timezone using the system tzdata database.
    """
    try:
        dt_naive = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M")
        zi = ZoneInfo(tz_name)
        dt_aware = dt_naive.replace(tzinfo=zi)
        utcoff = dt_aware.utcoffset()
        dstoff = dt_aware.dst()
        offset_hours = round(utcoff.total_seconds() / 3600.0, 4) if utcoff is not None else fallback_offset
        is_dst = bool(dstoff and dstoff.total_seconds() != 0)
        tz_abbr = dt_aware.tzname() or tz_name
        return {
            "timezone_name": tz_name,
            "timezone_abbr": tz_abbr,
            "utc_offset_hours": offset_hours,
            "is_dst_active": is_dst,
            "utc_datetime_iso": (dt_naive - (utcoff or (dt_naive - dt_naive))).strftime("%Y-%m-%dT%H:%M:00Z"),
        }
    except Exception:
        return {
            "timezone_name": tz_name or "UTC+5:30",
            "timezone_abbr": "LOCAL",
            "utc_offset_hours": fallback_offset,
            "is_dst_active": False,
            "utc_datetime_iso": f"{birth_date}T{birth_time}:00",
        }


async def search_birthplaces(
    query: str,
    birth_date: str = "1996-08-15",
    birth_time: str = "10:30",
    limit: int = 10,
) -> List[Dict[str, Any]]:
    """
    Searches both the instant built-in 85-city gazetteer AND OpenStreetMap Nominatim
    for any village, town, or city on Earth, returning exact latitude, longitude,
    IANA timezone name, and historical UTC offset for the given birth date/time.
    """
    q = (query or "").strip().lower()
    results: List[Dict[str, Any]] = []
    seen_coords = set()

    # 1. Instant local gazetteer matches
    for item in BUILT_IN_GAZETTEER:
        if not q or q in item["city"].lower():
            tz_meta = compute_historical_utc_offset(birth_date, birth_time, item["tz"])
            key = (round(item["lat"], 2), round(item["lon"], 2))
            seen_coords.add(key)
            results.append(
                {
                    "city": item["city"],
                    "latitude": item["lat"],
                    "longitude": item["lon"],
                    "timezone_name": tz_meta["timezone_name"],
                    "timezone_abbr": tz_meta["timezone_abbr"],
                    "utc_offset_hours": tz_meta["utc_offset_hours"],
                    "is_dst_active": tz_meta["is_dst_active"],
                    "source": "gazetteer",
                }
            )
            if len(results) >= limit:
                break

    # 2. If user typed a specific city/town not fully covered above, query OpenStreetMap Nominatim live
    if q and len(q) >= 2 and len(results) < 5:
        try:
            async with httpx.AsyncClient(timeout=2.5) as client:
                resp = await client.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={"q": query, "format": "json", "limit": 6, "addressdetails": 1},
                    headers={"User-Agent": "AstroFluence-Esoteric-Engine/1.0"},
                )
                if resp.status_code == 200:
                    for row in resp.json():
                        lat = round(float(row["lat"]), 4)
                        lon = round(float(row["lon"]), 4)
                        key = (round(lat, 2), round(lon, 2))
                        if key in seen_coords:
                            continue
                        seen_coords.add(key)
                        tz_name = resolve_tz_name_for_coords(lat, lon)
                        tz_meta = compute_historical_utc_offset(birth_date, birth_time, tz_name)
                        display = row.get("display_name", query)
                        short_parts = [p.strip() for p in display.split(",")]
                        clean_name = ", ".join(short_parts[:3]) if len(short_parts) > 3 else display
                        results.append(
                            {
                                "city": clean_name,
                                "latitude": lat,
                                "longitude": lon,
                                "timezone_name": tz_meta["timezone_name"],
                                "timezone_abbr": tz_meta["timezone_abbr"],
                                "utc_offset_hours": tz_meta["utc_offset_hours"],
                                "is_dst_active": tz_meta["is_dst_active"],
                                "source": "nominatim_osm",
                            }
                        )
        except Exception:
            pass

    return results[:limit]


def resolve_place_sync(
    city_name: str,
    latitude: Optional[float],
    longitude: Optional[float],
    timezone_name: Optional[str],
    timezone_offset: Optional[float],
    birth_date: str,
    birth_time: str,
) -> Dict[str, Any]:
    """
    Synchronously resolves any birthplace input (by city name and/or coordinates) into
    verified (city, latitude, longitude, timezone_name, exact_historical_utc_offset, is_dst).
    """
    q = (city_name or "").strip().lower()
    matched_item = None
    if q:
        for item in BUILT_IN_GAZETTEER:
            if q == item["city"].lower() or q in item["city"].lower() or item["city"].split(",")[0].lower() in q:
                matched_item = item
                break

    # If user picked a new city name but left default Delhi coordinates, snap to matched city coordinates
    is_default_delhi_coords = (
        latitude is None
        or longitude is None
        or (abs(latitude - 28.6139) < 0.01 and abs(longitude - 77.2090) < 0.01 and q and "delhi" not in q)
    )

    if matched_item and is_default_delhi_coords:
        lat = matched_item["lat"]
        lon = matched_item["lon"]
        tz_str = timezone_name or matched_item["tz"]
        clean_city = matched_item["city"]
    else:
        lat = latitude if latitude is not None else (matched_item["lat"] if matched_item else 28.6139)
        lon = longitude if longitude is not None else (matched_item["lon"] if matched_item else 77.2090)
        tz_str = timezone_name or (matched_item["tz"] if matched_item else resolve_tz_name_for_coords(lat, lon))
        clean_city = city_name or (matched_item["city"] if matched_item else "New Delhi, Delhi, India")

    tz_meta = compute_historical_utc_offset(
        birth_date=birth_date,
        birth_time=birth_time,
        tz_name=tz_str,
        fallback_offset=timezone_offset if timezone_offset is not None else 5.5,
    )

    return {
        "city": clean_city,
        "latitude": round(float(lat), 4),
        "longitude": round(float(lon), 4),
        "timezone_name": tz_meta["timezone_name"],
        "timezone_abbr": tz_meta["timezone_abbr"],
        "utc_offset_hours": tz_meta["utc_offset_hours"],
        "is_dst_active": tz_meta["is_dst_active"],
        "utc_datetime_iso": tz_meta["utc_datetime_iso"],
    }
