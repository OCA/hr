# Copyright 2026 Forgeflow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
# pylint: disable=W8161

import os

import swisseph as swe

from odoo.tools.translate import LazyTranslate

_lt = LazyTranslate(__name__)

_EPHE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ephe")
swe.set_ephe_path(_EPHE_PATH)

SIGNS = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]
SIGN_SYMBOLS = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]
# Keep as plain English — used as dictionary keys in interpretation logic
SIGN_ELEMENTS = ["Fire", "Earth", "Air", "Water"] * 3
SIGN_MODALITIES = ["Cardinal", "Fixed", "Mutable"] * 4
SIGN_POLARITIES = ["Positive", "Negative"] * 6

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


def compute_chart(year, month, day, hour=12.0, lat=None, lon=None):
    """Compute full birth chart using Swiss Ephemeris (Moshier fallback)."""
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
