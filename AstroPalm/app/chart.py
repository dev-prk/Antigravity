"""Chart engine: geocoding, historical timezone, Vedic and Western charts.

All positions come from the Swiss Ephemeris (built-in Moshier ephemeris, no data files).
"""
from __future__ import annotations

import datetime as dt
from functools import lru_cache
from zoneinfo import ZoneInfo

import swisseph as swe
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra",
         "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
SIGN_LORD = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus",
             "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]
NAKSHATRAS = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
              "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
              "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha",
              "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana",
              "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"]
DASHA_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
DASHA_YEARS = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
               "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}
NAK_SPAN = 360 / 27
YEAR_DAYS = 365.25

EXALT = {"Sun": 0, "Moon": 1, "Mars": 9, "Mercury": 5, "Jupiter": 3, "Venus": 11, "Saturn": 6}
OWN = {"Sun": [4], "Moon": [3], "Mars": [0, 7], "Mercury": [2, 5], "Jupiter": [8, 11],
       "Venus": [1, 6], "Saturn": [9, 10]}

CLASSICAL = [("Sun", swe.SUN), ("Moon", swe.MOON), ("Mars", swe.MARS), ("Mercury", swe.MERCURY),
             ("Jupiter", swe.JUPITER), ("Venus", swe.VENUS), ("Saturn", swe.SATURN)]
OUTER = [("Uranus", swe.URANUS), ("Neptune", swe.NEPTUNE), ("Pluto", swe.PLUTO)]

BASE_FLAGS = swe.FLG_MOSEPH | swe.FLG_SPEED

_tf = TimezoneFinder()
_geo = Nominatim(user_agent="astropalm-local-app", timeout=10)


# ---------------------------------------------------------------- places & time
@lru_cache(maxsize=256)
def search_places(query: str) -> list[dict]:
    """Return up to 6 candidate places so the user can pick the exact birthplace."""
    results = _geo.geocode(query, exactly_one=False, limit=6, language="en", addressdetails=False) or []
    out = []
    for r in results:
        tz = _tf.timezone_at(lng=r.longitude, lat=r.latitude)
        if tz:
            out.append({"name": r.address, "lat": round(r.latitude, 4),
                        "lon": round(r.longitude, 4), "tz": tz})
    return out


def to_utc(date: str, time: str | None, lat: float, lon: float, tz: str) -> dict:
    """Local birth date/time -> UTC using the historical offset for that exact date.

    Before standard time existed, zoneinfo reports 'LMT' of the zone's main city; we
    instead use true Local Mean Time of the birthplace itself (longitude / 15)."""
    t = time or "12:00"
    local = dt.datetime.fromisoformat(f"{date}T{t}")
    aware = local.replace(tzinfo=ZoneInfo(tz))
    if aware.tzname() == "LMT":
        offset = dt.timedelta(hours=lon / 15)
        note = f"Local Mean Time of birthplace (UTC{offset.total_seconds()/3600:+.2f}h)"
    else:
        offset = aware.utcoffset()
        dst = bool(aware.dst())
        note = f"{aware.tzname()} UTC{offset.total_seconds()/3600:+.2f}h" + (" (daylight saving in effect)" if dst else "")
    utc = (local - offset).replace(tzinfo=dt.timezone.utc)
    return {"utc": utc, "offset_note": note}


def julday(utc: dt.datetime) -> float:
    return swe.julday(utc.year, utc.month, utc.day,
                      utc.hour + utc.minute / 60 + utc.second / 3600)


# ---------------------------------------------------------------- helpers
def sign_of(lon: float) -> int:
    return int(lon // 30) % 12


def fmt_deg(lon: float) -> str:
    d = lon % 30
    return f"{int(d)}°{int((d % 1) * 60):02d}'"


def nakshatra(lon: float) -> dict:
    i = int(lon // NAK_SPAN)
    pada = int((lon % NAK_SPAN) // (NAK_SPAN / 4)) + 1
    return {"name": NAKSHATRAS[i], "pada": pada, "lord": DASHA_ORDER[i % 9]}


def dignity(planet: str, s: int) -> str:
    if planet in EXALT:
        if EXALT[planet] == s:
            return "exalted"
        if (EXALT[planet] + 6) % 12 == s:
            return "debilitated"
        if s in OWN[planet]:
            return "own sign"
    return ""


def positions(jd: float, sidereal: bool, bodies) -> dict:
    flags = BASE_FLAGS | (swe.FLG_SIDEREAL if sidereal else 0)
    out = {}
    for name, pid in bodies:
        xx, _ = swe.calc_ut(jd, pid, flags)
        out[name] = {"lon": xx[0] % 360, "retro": xx[3] < 0}
    return out


def _set_sidereal():
    swe.set_sid_mode(swe.SIDM_LAHIRI)


def next_ingress(jd_start: float, pid: int, sidereal: bool, max_days: int = 1500) -> str | None:
    """Date the planet next enters a new sign (first crossing)."""
    flags = BASE_FLAGS | (swe.FLG_SIDEREAL if sidereal else 0)
    s0 = sign_of(swe.calc_ut(jd_start, pid, flags)[0][0])
    for d in range(1, max_days):
        s = sign_of(swe.calc_ut(jd_start + d, pid, flags)[0][0])
        if s != s0:
            y, m, day, _ = swe.revjul(jd_start + d)
            return f"{y:04d}-{m:02d}-{day:02d} (enters {SIGNS[s]})"
    return None


def jd_to_date(jd: float) -> str:
    y, m, d, _ = swe.revjul(jd)
    return f"{y:04d}-{m:02d}-{d:02d}"


# ---------------------------------------------------------------- Vedic
def vimshottari(moon_lon: float, jd_birth: float, jd_now: float) -> dict:
    i = int(moon_lon // NAK_SPAN)
    lord_idx = i % 9
    frac = (moon_lon % NAK_SPAN) / NAK_SPAN
    start = jd_birth - frac * DASHA_YEARS[DASHA_ORDER[lord_idx]] * YEAR_DAYS
    periods = []  # (maha, antar, start, end)
    t = start
    for k in range(18):  # two full cycles = 240 years
        maha = DASHA_ORDER[(lord_idx + k) % 9]
        my = DASHA_YEARS[maha]
        a_t = t
        for j in range(9):
            antar = DASHA_ORDER[(DASHA_ORDER.index(maha) + j) % 9]
            length = my * DASHA_YEARS[antar] / 120 * YEAR_DAYS
            periods.append((maha, antar, a_t, a_t + length))
            a_t += length
        t += my * YEAR_DAYS
        if t > jd_now + 40 * YEAR_DAYS:
            break
    cur = next(p for p in periods if p[2] <= jd_now < p[3])
    idx = periods.index(cur)
    k = idx
    while k + 1 < len(periods) and periods[k + 1][0] == cur[0]:
        k += 1
    maha_end = periods[k][3]
    upcoming = [{"mahadasha": p[0], "antardasha": p[1], "from": jd_to_date(p[2]), "to": jd_to_date(p[3])}
                for p in periods[idx + 1: idx + 5]]
    return {
        "current": {"mahadasha": cur[0], "antardasha": cur[1],
                    "antardasha_from": jd_to_date(cur[2]), "antardasha_to": jd_to_date(cur[3]),
                    "mahadasha_ends": jd_to_date(maha_end)},
        "upcoming": upcoming,
    }


def vedic_chart(jd: float, lat: float, lon: float, time_known: bool, jd_now: float) -> dict:
    _set_sidereal()
    bodies = CLASSICAL + [("Rahu", swe.MEAN_NODE)]
    pos = positions(jd, True, bodies)
    pos["Ketu"] = {"lon": (pos["Rahu"]["lon"] + 180) % 360, "retro": True}
    pos["Rahu"]["retro"] = True

    chart = {"system": "Vedic (sidereal, Lahiri ayanamsa, whole-sign houses, mean nodes)",
             "ayanamsa": round(swe.get_ayanamsa_ut(jd), 4)}
    lagna_sign = None
    if time_known:
        _, ascmc = swe.houses_ex(jd, lat, lon, b"W", swe.FLG_SIDEREAL)
        asc = ascmc[0] % 360
        lagna_sign = sign_of(asc)
        chart["lagna"] = {"sign": SIGNS[lagna_sign], "degree": fmt_deg(asc), "nakshatra": nakshatra(asc)}

    planets = {}
    for name, p in pos.items():
        s = sign_of(p["lon"])
        planets[name] = {
            "sign": SIGNS[s], "degree": fmt_deg(p["lon"]), "nakshatra": nakshatra(p["lon"]),
            "retrograde": p["retro"] if name not in ("Rahu", "Ketu") else False,
            "dignity": dignity(name, s),
            "house": ((s - lagna_sign) % 12 + 1) if lagna_sign is not None else None,
        }
    chart["planets"] = planets
    moon_sign = sign_of(pos["Moon"]["lon"])
    chart["moon_sign_rashi"] = SIGNS[moon_sign]
    chart["janma_nakshatra"] = nakshatra(pos["Moon"]["lon"])
    if lagna_sign is not None:
        chart["house_lords"] = {str(h): {"sign": SIGNS[(lagna_sign + h - 1) % 12],
                                         "lord": SIGN_LORD[(lagna_sign + h - 1) % 12]} for h in range(1, 13)}
    chart["dasha"] = vimshottari(pos["Moon"]["lon"], jd, jd_now)

    # Current transits (gochara), counted from Moon (and Lagna if known)
    now = positions(jd_now, True, [("Saturn", swe.SATURN), ("Jupiter", swe.JUPITER), ("Rahu", swe.MEAN_NODE)])
    now["Ketu"] = {"lon": (now["Rahu"]["lon"] + 180) % 360, "retro": True}
    tr = {}
    for name, p in now.items():
        s = sign_of(p["lon"])
        tr[name] = {"sign": SIGNS[s], "house_from_moon": (s - moon_sign) % 12 + 1,
                    "house_from_lagna": ((s - lagna_sign) % 12 + 1) if lagna_sign is not None else None,
                    "retrograde": p["retro"] if name in ("Saturn", "Jupiter") else False}
    tr["Saturn"]["next_sign_change"] = next_ingress(jd_now, swe.SATURN, True)
    tr["Jupiter"]["next_sign_change"] = next_ingress(jd_now, swe.JUPITER, True)
    h = tr["Saturn"]["house_from_moon"]
    tr["saturn_phase"] = {12: "Sade Sati — rising phase (Saturn 12th from Moon)",
                          1: "Sade Sati — peak phase (Saturn over natal Moon)",
                          2: "Sade Sati — setting phase (Saturn 2nd from Moon)",
                          8: "Ashtama Shani (Saturn 8th from Moon)",
                          4: "Kantaka/Ardhashtama Shani (Saturn 4th from Moon)"}.get(h, "No Sade Sati / Ashtama Shani now")
    chart["current_transits"] = tr

    if not time_known:
        chart["time_unknown_notes"] = _unknown_time_moon_note(jd, True)
    return chart


# ---------------------------------------------------------------- Western
ASPECTS = [(0, "conjunct", 8), (60, "sextile", 4), (90, "square", 6), (120, "trine", 6), (180, "opposite", 7)]
TRANSIT_ASPECTS = [(0, "conjunct"), (90, "square"), (120, "trine"), (180, "opposite")]


def _aspect(a: float, b: float, table):
    diff = abs((a - b + 180) % 360 - 180)
    for item in table:
        angle, name = item[0], item[1]
        orb = item[2] if len(item) > 2 else 2.5
        if abs(diff - angle) <= orb:
            return name, round(abs(diff - angle), 1)
    return None


def western_chart(jd: float, lat: float, lon: float, time_known: bool, jd_now: float) -> dict:
    bodies = CLASSICAL + OUTER + [("North Node", swe.MEAN_NODE)]
    pos = positions(jd, False, bodies)
    chart = {"system": "Western (tropical zodiac, Placidus houses)"}
    cusps = None
    points = dict((k, v["lon"]) for k, v in pos.items())
    if time_known:
        hsys = b"P" if abs(lat) < 66 else b"W"
        cusps, ascmc = swe.houses_ex(jd, lat, lon, hsys, 0)
        asc, mc = ascmc[0] % 360, ascmc[1] % 360
        chart["ascendant"] = {"sign": SIGNS[sign_of(asc)], "degree": fmt_deg(asc)}
        chart["midheaven"] = {"sign": SIGNS[sign_of(mc)], "degree": fmt_deg(mc)}
        if hsys == b"W":
            chart["system"] += " (whole-sign used: polar latitude)"
        points["Ascendant"], points["Midheaven"] = asc, mc

    def house_of(l):
        if not cusps:
            return None
        for i in range(12):
            a, b = cusps[i], cusps[(i + 1) % 12]
            if (l - a) % 360 < (b - a) % 360:
                return i + 1
        return None

    chart["planets"] = {n: {"sign": SIGNS[sign_of(p["lon"])], "degree": fmt_deg(p["lon"]),
                            "retrograde": p["retro"] and n != "North Node",
                            "house": house_of(p["lon"])} for n, p in pos.items()}
    if cusps:
        chart["house_cusps"] = {str(i + 1): f"{SIGNS[sign_of(c)]} {fmt_deg(c)}" for i, c in enumerate(cusps)}

    names = [n for n, _ in CLASSICAL]
    natal_aspects = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            r = _aspect(pos[a]["lon"], pos[b]["lon"], ASPECTS)
            if r:
                natal_aspects.append(f"{a} {r[0]} {b} (orb {r[1]}°)")
    chart["natal_aspects"] = natal_aspects

    now = positions(jd_now, False, [("Jupiter", swe.JUPITER), ("Saturn", swe.SATURN)] + OUTER + [("North Node", swe.MEAN_NODE)])
    targets = {k: points[k] for k in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Saturn", "Ascendant", "Midheaven"] if k in points}
    transits = []
    for tn, tp in now.items():
        for nn, nl in targets.items():
            r = _aspect(tp["lon"], nl, TRANSIT_ASPECTS)
            if r:
                transits.append(f"Transiting {tn} {r[0]} natal {nn} (orb {r[1]}°)")
    chart["current_transits"] = {
        "positions": {n: {"sign": SIGNS[sign_of(p["lon"])], "degree": fmt_deg(p["lon"]),
                          "retrograde": p["retro"] and n != "North Node", "natal_house": house_of(p["lon"])}
                      for n, p in now.items()},
        "aspects_to_natal": transits or ["No major slow-planet aspects to natal points within orb right now"],
        "saturn_next_sign_change": next_ingress(jd_now, swe.SATURN, False),
        "jupiter_next_sign_change": next_ingress(jd_now, swe.JUPITER, False),
    }
    if not time_known:
        chart["time_unknown_notes"] = _unknown_time_moon_note(jd, False)
    return chart


def _unknown_time_moon_note(jd_noon: float, sidereal: bool) -> list[str]:
    flags = BASE_FLAGS | (swe.FLG_SIDEREAL if sidereal else 0)
    m0 = swe.calc_ut(jd_noon - 0.5, swe.MOON, flags)[0][0]
    m1 = swe.calc_ut(jd_noon + 0.5, swe.MOON, flags)[0][0]
    notes = ["Birth time unknown: chart cast for 12:00 local. Ascendant, houses and house lords are NOT available; "
             "do not make house-based claims."]
    if sign_of(m0) != sign_of(m1):
        notes.append(f"Moon changed sign that day ({SIGNS[sign_of(m0)]} → {SIGNS[sign_of(m1)]}); Moon sign is uncertain.")
    if sidereal and int(m0 // NAK_SPAN) != int(m1 // NAK_SPAN):
        notes.append(f"Moon changed nakshatra that day ({NAKSHATRAS[int(m0 // NAK_SPAN)]} → "
                     f"{NAKSHATRAS[int(m1 // NAK_SPAN)]}); nakshatra and dasha dates are approximate.")
    return notes


# ---------------------------------------------------------------- entry point
def build_chart(system: str, date: str, time: str | None, lat: float, lon: float, tz: str,
                now: dt.datetime | None = None) -> dict:
    t = to_utc(date, time, lat, lon, tz)
    jd = julday(t["utc"])
    now = now or dt.datetime.now(dt.timezone.utc)
    jd_now = julday(now)
    time_known = bool(time)
    fn = vedic_chart if system == "vedic" else western_chart
    chart = fn(jd, lat, lon, time_known, jd_now)
    chart["birth"] = {"local": f"{date} {time or 'time unknown'}", "utc": t["utc"].strftime("%Y-%m-%d %H:%M UTC"),
                      "timezone": f"{tz} — {t['offset_note']}", "lat": lat, "lon": lon}
    chart["computed_on"] = now.strftime("%Y-%m-%d")
    return chart
