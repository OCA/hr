# Copyright 2026 Forgeflow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
# pylint: disable=W8161

import os
import threading

import pytz
import swisseph as swe
from timezonefinder import TimezoneFinder

from odoo.tools.translate import LazyTranslate

_lt = LazyTranslate(__name__)

_EPHE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ephe")
swe.set_ephe_path(_EPHE_PATH)

SIGNS = [
    _lt("Aries"),
    _lt("Taurus"),
    _lt("Gemini"),
    _lt("Cancer"),
    _lt("Leo"),
    _lt("Virgo"),
    _lt("Libra"),
    _lt("Scorpio"),
    _lt("Sagittarius"),
    _lt("Capricorn"),
    _lt("Aquarius"),
    _lt("Pisces"),
]
SIGN_SYMBOLS = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]
# Keep as plain English — used as dictionary keys in interpretation logic
SIGN_ELEMENTS = ["Fire", "Earth", "Air", "Water"] * 3
SIGN_MODALITIES = ["Cardinal", "Fixed", "Mutable"] * 4
SIGN_POLARITIES = ["Positive", "Negative"] * 6

# ...so these hold their translatable display labels
ELEMENT_LABELS = {
    "Fire": _lt("Fire"),
    "Earth": _lt("Earth"),
    "Air": _lt("Air"),
    "Water": _lt("Water"),
}
MODALITY_LABELS = {
    "Cardinal": _lt("Cardinal"),
    "Fixed": _lt("Fixed"),
    "Mutable": _lt("Mutable"),
}
POLARITY_LABELS = {
    "Positive": _lt("Positive"),
    "Negative": _lt("Negative"),
}

# Lazily translated: rendered with env._() wherever they are displayed
PLANET_NAMES = [
    _lt("Sun"),
    _lt("Moon"),
    _lt("Mercury"),
    _lt("Venus"),
    _lt("Mars"),
    _lt("Jupiter"),
    _lt("Saturn"),
    _lt("Uranus"),
    _lt("Neptune"),
    _lt("Pluto"),
    _lt("Chiron"),
    _lt("Lilith"),
    _lt("Ceres"),
]
PLANET_SYMBOLS = ["☉", "☽", "☿", "♀", "♂", "♃", "♄", "⛢", "♆", "♇", "⚷", "⚸", "⚳"]
PLANET_KEYS = [
    "sun",
    "moon",
    "mercury",
    "venus",
    "mars",
    "jupiter",
    "saturn",
    "uranus",
    "neptune",
    "pluto",
    "chiron",
    "lilith",
    "ceres",
]

_SWE_IDS = {
    "sun": swe.SUN,
    "moon": swe.MOON,
    "mercury": swe.MERCURY,
    "venus": swe.VENUS,
    "mars": swe.MARS,
    "jupiter": swe.JUPITER,
    "saturn": swe.SATURN,
    "uranus": swe.URANUS,
    "neptune": swe.NEPTUNE,
    "pluto": swe.PLUTO,
    "chiron": swe.CHIRON,
    "lilith": swe.MEAN_APOG,
    "ceres": swe.CERES,
}

# Chiron and Ceres require seas_18.se1; all others work via Moshier fallback.
_NEEDS_SE_FILE = {"chiron", "ceres"}
_FLAGS_SE = swe.FLG_SWIEPH
_FLAGS_MOSH = swe.FLG_MOSEPH


def _norm(deg):
    return deg % 360.0


def lon_to_sign(lon):
    """Return (sign_index, degrees_in_sign, minutes)."""
    idx = int(lon / 30) % 12
    deg_in = lon % 30
    return idx, int(deg_in), int((deg_in % 1) * 60)


def get_house(lon, houses):
    """Return 1-based house number for a longitude given Whole Sign houses."""
    if not houses:
        return None
    for h_i in range(12):
        cusp_start = houses[h_i]
        cusp_end = houses[(h_i + 1) % 12]
        if cusp_start <= cusp_end:
            in_house = cusp_start <= lon < cusp_end
        else:
            in_house = lon >= cusp_start or lon < cusp_end
        if in_house:
            return h_i + 1
    return None


ASPECT_DEFS = [
    ("Conjunction", 0, 8, "☌", "#cc3333"),
    ("Sextile", 60, 5, "⚹", "#44aa44"),
    ("Square", 90, 7, "□", "#cc6633"),
    ("Trine", 120, 7, "△", "#4466cc"),
    ("Opposition", 180, 8, "☍", "#aa3399"),
]

# Aspect names stay plain English because they are used as dictionary keys in
# the interpretation tables; these are their translatable display labels.
ASPECT_LABELS = {
    "Conjunction": _lt("Conjunction"),
    "Sextile": _lt("Sextile"),
    "Square": _lt("Square"),
    "Trine": _lt("Trine"),
    "Opposition": _lt("Opposition"),
}


def calc_aspects(natal_planets, transit_planets):
    """Return list of active aspects between transit and natal planets."""
    aspects = []
    for t_key in PLANET_KEYS:
        t_lon = transit_planets[t_key]
        for n_key in PLANET_KEYS:
            n_lon = natal_planets[n_key]
            diff = abs((t_lon - n_lon + 180) % 360 - 180)
            for name, angle, orb, symbol, color in ASPECT_DEFS:
                if abs(diff - angle) <= orb:
                    aspects.append(
                        {
                            "transit_key": t_key,
                            "natal_key": n_key,
                            "aspect": name,
                            "symbol": symbol,
                            "color": color,
                            "orb": round(abs(diff - angle), 1),
                        }
                    )
    return aspects


# The library asks for one instance per thread rather than a shared one
_tz_finder = threading.local()


def timezone_at(lat, lon):
    """Return the timezone of a coordinate pair, or None if there is none."""
    finder = getattr(_tz_finder, "finder", None)
    if finder is None:
        finder = _tz_finder.finder = TimezoneFinder()
    name = finder.timezone_at(lat=lat, lng=lon)
    return pytz.timezone(name) if name else None


def country_timezone(country_code, naive):
    """Return a country's timezone, but only when it is not a guess.

    A country can span several zones, so one is returned only if every zone that
    country uses was on the same UTC offset at ``naive``. That makes the offset
    a fact: Italy always resolves, Germany resolves because Büsingen kept
    Berlin's offset on that date, and Spain never does because the Canaries run
    an hour behind the mainland. 216 countries have a single zone to begin with.

    Beware that this fixes the time, not the place: the Ascendant and the houses
    still need real coordinates.
    """
    zones = [
        pytz.timezone(name) for name in pytz.country_timezones.get(country_code, ())
    ]
    if not zones:
        return None
    offsets = {zone.localize(naive, is_dst=False).utcoffset() for zone in zones}
    return zones[0] if len(offsets) == 1 else None


def local_to_ut(naive, zone):
    """Turn a local clock time into Universal Time.

    A birth time is the local clock time where the birth happened, while the
    ephemeris works in Universal Time. The rules in force on that very date are
    applied, historical daylight saving included, so this cannot be replaced by
    a fixed offset. An ambiguous local time, the hour that repeats when clocks
    go back, is read as standard time.

    :return: ``(year, month, day, decimal_hour)`` in UT.
    """
    ut = zone.localize(naive, is_dst=False).astimezone(pytz.utc)
    return ut.year, ut.month, ut.day, ut.hour + ut.minute / 60 + ut.second / 3600


def compute_chart(year, month, day, hour=12.0, lat=None, lon=None):
    """Compute full birth chart using Swiss Ephemeris (Moshier fallback).

    ``hour`` is decimal **Universal Time**, not local clock time: run a birth
    time through :func:`local_to_ut` first. Feeding local time straight in
    misplaces the Ascendant by about 15 degrees per hour of offset.
    """
    swe.set_ephe_path(_EPHE_PATH)
    jd = swe.julday(year, month, day, hour)

    planets = {}
    for key in PLANET_KEYS:
        flags = _FLAGS_SE if key in _NEEDS_SE_FILE else _FLAGS_MOSH
        result, _ = swe.calc_ut(jd, _SWE_IDS[key], flags)
        planets[key] = _norm(result[0])

    nn_result, _ = swe.calc_ut(jd, swe.MEAN_NODE, _FLAGS_MOSH)
    north_node = _norm(nn_result[0])

    chart = {"planets": planets, "jd": jd, "north_node": north_node}

    if lat is not None and lon is not None:
        cusps, ascmc = swe.houses(jd, lat, lon, b"W")
        chart["ascendant"] = _norm(ascmc[0])
        chart["midheaven"] = _norm(ascmc[1])
        chart["houses"] = [_norm(c) for c in cusps[0:12]]
    else:
        chart["ascendant"] = None
        chart["midheaven"] = None
        chart["houses"] = None

    return chart
