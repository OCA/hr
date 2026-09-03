# Copyright 2026 Forgeflow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
# pylint: disable=W8161

import math

from .astro_calc import (
    PLANET_KEYS,
    PLANET_NAMES,
    PLANET_SYMBOLS,
    SIGN_SYMBOLS,
    SIGNS,
    get_house,
    lon_to_sign,
)

CX, CY, R = 260, 260, 200
R_SIGN = R
R_SIGN_IN = R - 36
R_HOUSE = R_SIGN_IN - 4
R_PLANET = R_HOUSE - 22
R_CENTER = R_PLANET - 28

R_TRANSIT_OUT = R_SIGN + 36
R_TRANSIT_IN = R_SIGN + 4
R_TRANSIT_PLANET = R_SIGN + 20

COLOR_FIRE = "#e8554e"
COLOR_EARTH = "#7db87d"
COLOR_AIR = "#7ba7c7"
COLOR_WATER = "#9b7fc0"
SIGN_COLORS = [COLOR_FIRE, COLOR_EARTH, COLOR_AIR, COLOR_WATER] * 3
PLANET_COLORS = {
    "sun": "#e8a020",
    "moon": "#8888cc",
    "mercury": "#44aa88",
    "venus": "#cc6688",
    "mars": "#cc3333",
    "jupiter": "#8866cc",
    "saturn": "#888844",
    "uranus": "#44aacc",
    "neptune": "#4466cc",
    "pluto": "#884422",
    "chiron": "#5fa8a0",
    "lilith": "#776688",
    "ceres": "#6a9e5a",
}

# CSS embedded in the SVG — uses Bootstrap/Odoo CSS variables so the chart
# adapts automatically to light mode, dark mode and custom themes.
_SVG_STYLE = """<style>
  .bc-bg     { fill: var(--bs-body-bg, #fff); }
  .bc-rim    { fill: none; stroke: var(--bs-border-color, #999); }
  .bc-sector { stroke: var(--bs-border-color, #999); stroke-width: .5; }
  .bc-spoke  { fill: none; stroke: var(--bs-border-color, #999); stroke-width: .5; }
  .bc-hl     { stroke: var(--bs-border-color, #777); }
  .bc-hn     { fill: var(--bs-secondary-color, #888); font-size: 9px;
               text-anchor: middle; dominant-baseline: central; }
  .bc-ac     { fill: #d4a017; font-size: 9px; font-weight: bold;
               text-anchor: middle; dominant-baseline: central; }
  .bc-mc     { fill: #5599cc; font-size: 9px; font-weight: bold;
               text-anchor: middle; dominant-baseline: central; }
</style>"""


def _r(deg):
    return math.radians(deg)


def _xy(angle_deg, r, cx=CX, cy=CY):
    a = math.radians(180.0 - angle_deg)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def _sign_sector(i):
    start, end = i * 30, (i + 1) * 30
    x1o, y1o = _xy(start, R_SIGN)
    x2o, y2o = _xy(end, R_SIGN)
    x1i, y1i = _xy(start, R_SIGN_IN)
    x2i, y2i = _xy(end, R_SIGN_IN)
    return (
        f"M {x1o:.2f} {y1o:.2f} "
        f"A {R_SIGN} {R_SIGN} 0 0 0 {x2o:.2f} {y2o:.2f} "
        f"L {x2i:.2f} {y2i:.2f} "
        f"A {R_SIGN_IN} {R_SIGN_IN} 0 0 1 {x1i:.2f} {y1i:.2f} Z"
    )


def _spoke(angle_deg):
    x1, y1 = _xy(angle_deg, R_SIGN)
    x2, y2 = _xy(angle_deg, R_SIGN_IN)
    return f"M {x1:.2f} {y1:.2f} L {x2:.2f} {y2:.2f}"


def _render_zodiac_ring(parts, r_out, r_in, xy_fn, opacity, font_size):
    """Render a 12-sector zodiac ring with sign symbols and boundary spokes."""
    for i in range(12):
        s, e = i * 30, (i + 1) * 30
        x1o, y1o = xy_fn(s, r_out)
        x2o, y2o = xy_fn(e, r_out)
        x1i, y1i = xy_fn(s, r_in)
        x2i, y2i = xy_fn(e, r_in)
        d = (
            f"M {x1o:.2f} {y1o:.2f} "
            f"A {r_out} {r_out} 0 0 0 {x2o:.2f} {y2o:.2f} "
            f"L {x2i:.2f} {y2i:.2f} "
            f"A {r_in} {r_in} 0 0 1 {x1i:.2f} {y1i:.2f} Z"
        )
        parts.append(
            f'<path d="{d}" fill="{SIGN_COLORS[i]}" '
            f'fill-opacity="{opacity}" class="bc-sector"/>'
        )
        mid = i * 30 + 15
        sx, sy = xy_fn(mid, (r_out + r_in) / 2)
        parts.append(
            f'<text x="{sx:.1f}" y="{sy:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" font-size="{font_size}" '
            f'fill="{SIGN_COLORS[i]}">{SIGN_SYMBOLS[i]}</text>'
        )
    for i in range(12):
        x1, y1 = xy_fn(i * 30, r_out)
        x2, y2 = xy_fn(i * 30, r_in)
        parts.append(
            f'<path d="M {x1:.2f} {y1:.2f} L {x2:.2f} {y2:.2f}" class="bc-spoke"/>'
        )


def _place_planets(planets, planet_keys, min_gap_deg):
    """Return list of (adjusted_angle, key) with overlap avoidance."""
    placed = []
    for key in planet_keys:
        adj = planets[key]
        for prev_adj, _k in placed:
            if abs((adj - prev_adj + 180) % 360 - 180) < min_gap_deg:
                adj = prev_adj + min_gap_deg + 1
        placed.append((adj, key))
    return placed


def _render_planet_ring(
    parts,
    placed,
    planets,
    tick_r,
    planet_r,
    colors,
    symbols,
    xy_fn,
    font_size,
    inner_tick=True,
):
    """Render planet tick marks, offset leader lines, and symbol labels."""
    for adj, key in placed:
        orig = planets[key]
        col = colors[key]
        sym = symbols[PLANET_KEYS.index(key)]
        px, py = xy_fn(adj, planet_r)
        tx1, ty1 = xy_fn(orig, tick_r - 2)
        tx2, ty2 = xy_fn(orig, tick_r + 2)
        parts.append(
            f'<line x1="{tx1:.2f}" y1="{ty1:.2f}" '
            f'x2="{tx2:.2f}" y2="{ty2:.2f}" '
            f'stroke="{col}" stroke-width="1.5" fill="none"/>'
        )
        if abs((adj - orig + 180) % 360 - 180) > 2:
            lx, ly = (tx1, ty1) if inner_tick else (tx2, ty2)
            parts.append(
                f'<line x1="{lx:.2f}" y1="{ly:.2f}" '
                f'x2="{px:.2f}" y2="{py:.2f}" '
                f'stroke="{col}" stroke-width="0.4" '
                f'stroke-dasharray="2,2" fill="none"/>'
            )
        parts.append(
            f'<text x="{px:.1f}" y="{py:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" font-size="{font_size}" '
            f'fill="{col}">{sym}</text>'
        )


def generate_chart_svg(chart_data):
    """Generate an SVG birth chart from compute_chart() output."""
    planets = chart_data["planets"]
    houses = chart_data.get("houses")
    asc = chart_data.get("ascendant")
    mc = chart_data.get("midheaven")

    W, H = 520, 520
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'style="font-family:serif;border-radius:50%;overflow:visible">',
        _SVG_STYLE,
    ]

    # ── Zodiac sectors ──────────────────────────────────────────────────────
    for i in range(12):
        parts.append(
            f'<path d="{_sign_sector(i)}" fill="{SIGN_COLORS[i]}" '
            f'fill-opacity="0.30" class="bc-sector"/>'
        )
        mid = i * 30 + 15
        sx, sy = _xy(mid, (R_SIGN + R_SIGN_IN) / 2)
        parts.append(
            f'<text x="{sx:.1f}" y="{sy:.1f}" text-anchor="middle" '
            f'dominant-baseline="central" font-size="13" '
            f'fill="{SIGN_COLORS[i]}">{SIGN_SYMBOLS[i]}</text>'
        )

    # Spokes between signs
    for i in range(12):
        parts.append(f'<path d="{_spoke(i * 30)}" class="bc-spoke"/>')

    # ── Ring circles ────────────────────────────────────────────────────────
    for rr, sw in ((R_SIGN, "1"), (R_SIGN_IN, ".8"), (R_HOUSE, ".5")):
        parts.append(
            f'<circle cx="{CX}" cy="{CY}" r="{rr}" class="bc-rim" stroke-width="{sw}"/>'
        )
    # Centre fill adapts to body background
    parts.append(
        f'<circle cx="{CX}" cy="{CY}" r="{R_CENTER}" '
        f'class="bc-bg bc-rim" stroke-width=".5"/>'
    )

    # ── House cusps ─────────────────────────────────────────────────────────
    if houses:
        for i, cusp in enumerate(houses):
            x1, y1 = _xy(cusp, R_HOUSE)
            x2, y2 = _xy(cusp, R_CENTER)
            cls = "bc-ac" if i == 0 else "bc-hl"
            sw = "1.5" if i in (0, 3, 6, 9) else "0.5"
            parts.append(
                f'<line x1="{x1:.2f}" y1="{y1:.2f}" '
                f'x2="{x2:.2f}" y2="{y2:.2f}" '
                f'class="{cls}" stroke-width="{sw}" '
                f'fill="none"/>'
            )
            mid_angle = cusp + 15
            nx, ny = _xy(mid_angle, (R_HOUSE + R_CENTER) / 2)
            parts.append(
                f'<text x="{nx:.1f}" y="{ny:.1f}" class="bc-hn">{i + 1}</text>'
            )

    # ── Planets ──────────────────────────────────────────────────────────────
    placed = _place_planets(planets, PLANET_KEYS, 12)
    _render_planet_ring(
        parts,
        placed,
        planets,
        R_HOUSE,
        R_PLANET,
        PLANET_COLORS,
        PLANET_SYMBOLS,
        _xy,
        14,
    )

    # ── AC / MC labels ────────────────────────────────────────────────────────
    if asc is not None:
        ax, ay = _xy(asc, R_HOUSE + 10)
        parts.append(f'<text x="{ax:.1f}" y="{ay:.1f}" class="bc-ac">AC</text>')
    if mc is not None:
        mx2, my2 = _xy(mc, R_HOUSE + 10)
        parts.append(f'<text x="{mx2:.1f}" y="{my2:.1f}" class="bc-mc">MC</text>')

    parts.append("</svg>")
    return "".join(parts)


def build_planet_table(env, chart_data):
    """Return a list of dicts for the planet position table."""
    planets = chart_data["planets"]
    houses = chart_data.get("houses")
    rows = []
    for key, name, sym in zip(PLANET_KEYS, PLANET_NAMES, PLANET_SYMBOLS, strict=False):
        lon = planets[key]
        sign_i, deg, minute = lon_to_sign(lon)
        rows.append(
            {
                "key": key,
                "name": env._(name),
                "symbol": sym,
                "longitude": round(lon, 2),
                "sign_index": sign_i,
                "sign": env._(SIGNS[sign_i]),
                "sign_symbol": SIGN_SYMBOLS[sign_i],
                "position": f"{deg}°{minute:02d}'",
                "house": get_house(lon, houses),
            }
        )

    extra = []
    if chart_data.get("ascendant") is not None:
        asc_lon = chart_data["ascendant"]
        sign_i, deg, minute = lon_to_sign(asc_lon)
        extra.append(
            {
                "key": "ascendant",
                "name": env._("Ascendant"),
                "symbol": "AC",
                "longitude": round(asc_lon, 2),
                "sign_index": sign_i,
                "sign": env._(SIGNS[sign_i]),
                "sign_symbol": SIGN_SYMBOLS[sign_i],
                "position": f"{deg}°{minute:02d}'",
                "house": 1,
            }
        )
    if chart_data.get("midheaven") is not None:
        mc_lon = chart_data["midheaven"]
        sign_i, deg, minute = lon_to_sign(mc_lon)
        extra.append(
            {
                "key": "midheaven",
                "name": env._("Midheaven (MC)"),
                "symbol": "MC",
                "longitude": round(mc_lon, 2),
                "sign_index": sign_i,
                "sign": env._(SIGNS[sign_i]),
                "sign_symbol": SIGN_SYMBOLS[sign_i],
                "position": f"{deg}°{minute:02d}'",
                "house": 10,
            }
        )
    if chart_data.get("north_node") is not None:
        nn_lon = chart_data["north_node"]
        sign_i, deg, minute = lon_to_sign(nn_lon)
        extra.append(
            {
                "key": "north_node",
                "name": env._("North Node"),
                "symbol": "☊",
                "longitude": round(nn_lon, 2),
                "sign_index": sign_i,
                "sign": env._(SIGNS[sign_i]),
                "sign_symbol": SIGN_SYMBOLS[sign_i],
                "position": f"{deg}°{minute:02d}'",
                "house": get_house(nn_lon, houses),
            }
        )
    return rows, extra


def build_houses_html(env, chart_data):
    """Return an HTML table of houses (Whole Sign), or empty string if no houses."""
    houses = chart_data.get("houses")
    if not houses:
        return ""
    planets = chart_data.get("planets", {})

    # Map each house number → list of (symbol, color) for bodies in that house
    house_bodies = {h: [] for h in range(1, 13)}
    for key, sym in zip(PLANET_KEYS, PLANET_SYMBOLS, strict=False):
        if key in planets:
            h = get_house(planets[key], houses)
            if h:
                house_bodies[h].append((sym, PLANET_COLORS[key]))
    if chart_data.get("north_node") is not None:
        h = get_house(chart_data["north_node"], houses)
        if h:
            house_bodies[h].append(("☊", "#888888"))

    rows = []
    for i, cusp in enumerate(houses):
        sign_i = int(cusp / 30) % 12
        bodies_html = "".join(
            f'<span style="color:{col};font-size:14px;margin-right:2px">{sym}</span>'
            for sym, col in house_bodies[i + 1]
        )
        rows.append(
            f"<tr>"
            f"<td class='py-1 fw-medium'>{i + 1}</td>"
            f"<td class='py-1'>"
            f"<span style='color:{SIGN_COLORS[sign_i]};font-size:15px'>"
            f"{SIGN_SYMBOLS[sign_i]}</span>"
            f"<span class='ms-1'>{env._(SIGNS[sign_i])}</span></td>"
            f"<td class='py-1'>{bodies_html}</td>"
            f"</tr>"
        )
    return (
        "<table class='table table-sm table-hover mb-0' style='width:auto'>"
        "<thead><tr class='text-muted' style='font-size:12px'>"
        f"<th style='min-width:40px'>{env._('House')}</th>"
        f"<th style='min-width:130px'>{env._('Sign')}</th>"
        f"<th>{env._('Planets')}</th>"
        "</tr></thead>"
        "<tbody>" + "".join(rows) + "</tbody>"
        "</table>"
    )


def generate_biwheel_svg(natal_data, transit_data, aspects=None):
    """Generate a bi-wheel SVG with natal (inner) and transit (outer) planets."""
    planets_n = natal_data["planets"]
    houses = natal_data.get("houses")
    asc = natal_data.get("ascendant")
    mc = natal_data.get("midheaven")
    planets_t = transit_data["planets"]

    W, H, CXB, CYB = 560, 560, 280, 280

    def xy(angle_deg, r):
        return _xy(angle_deg, r, cx=CXB, cy=CYB)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'style="font-family:serif;overflow:visible">',
        _SVG_STYLE,
    ]

    # ── Zodiac rings ──────────────────────────────────────────────────────────
    _render_zodiac_ring(parts, R_TRANSIT_OUT, R_TRANSIT_IN, xy, "0.15", 10)
    _render_zodiac_ring(parts, R_SIGN, R_SIGN_IN, xy, "0.30", 13)

    # ── Ring circles ─────────────────────────────────────────────────────────
    for rr, sw in (
        (R_TRANSIT_OUT, "1"),
        (R_TRANSIT_IN, ".8"),
        (R_SIGN, "1"),
        (R_SIGN_IN, ".8"),
        (R_HOUSE, ".5"),
    ):
        parts.append(
            f'<circle cx="{CXB}" cy="{CYB}" r="{rr}"'
            f' class="bc-rim" stroke-width="{sw}"/>'
        )
    parts.append(
        f'<circle cx="{CXB}" cy="{CYB}" r="{R_CENTER}" '
        f'class="bc-bg bc-rim" stroke-width=".5"/>'
    )

    # ── House cusps ──────────────────────────────────────────────────────────
    if houses:
        for i, cusp in enumerate(houses):
            x1, y1 = xy(cusp, R_HOUSE)
            x2, y2 = xy(cusp, R_CENTER)
            cls = "bc-ac" if i == 0 else "bc-hl"
            sw = "1.5" if i in (0, 3, 6, 9) else "0.5"
            parts.append(
                f'<line x1="{x1:.2f}" y1="{y1:.2f}" '
                f'x2="{x2:.2f}" y2="{y2:.2f}" '
                f'class="{cls}" stroke-width="{sw}" fill="none"/>'
            )
            mid_angle = cusp + 15
            nx, ny = xy(mid_angle, (R_HOUSE + R_CENTER) / 2)
            parts.append(
                f'<text x="{nx:.1f}" y="{ny:.1f}" class="bc-hn">{i + 1}</text>'
            )

    # ── Natal and transit planets ─────────────────────────────────────────────
    placed_n = _place_planets(planets_n, PLANET_KEYS, 12)
    _render_planet_ring(
        parts,
        placed_n,
        planets_n,
        R_HOUSE,
        R_PLANET,
        PLANET_COLORS,
        PLANET_SYMBOLS,
        xy,
        14,
    )

    placed_t = _place_planets(planets_t, PLANET_KEYS, 10)
    _render_planet_ring(
        parts,
        placed_t,
        planets_t,
        R_TRANSIT_IN,
        R_TRANSIT_PLANET,
        PLANET_COLORS,
        PLANET_SYMBOLS,
        xy,
        12,
        inner_tick=False,
    )

    # ── AC / MC labels ───────────────────────────────────────────────────────
    if asc is not None:
        ax, ay = xy(asc, R_HOUSE + 10)
        parts.append(f'<text x="{ax:.1f}" y="{ay:.1f}" class="bc-ac">AC</text>')
    if mc is not None:
        mx2, my2 = xy(mc, R_HOUSE + 10)
        parts.append(f'<text x="{mx2:.1f}" y="{my2:.1f}" class="bc-mc">MC</text>')

    # ── Aspect lines (tightest aspects only) ─────────────────────────────────
    if aspects:
        for asp in sorted(aspects, key=lambda a: a["orb"]):
            if asp["orb"] > 4:
                break
            n_lon = planets_n[asp["natal_key"]]
            t_lon = planets_t[asp["transit_key"]]
            nxp, nyp = xy(n_lon, R_CENTER - 4)
            txp, typ = xy(t_lon, R_TRANSIT_IN + 4)
            opacity = round(max(0.1, 0.45 - asp["orb"] * 0.08), 2)
            parts.append(
                f'<line x1="{nxp:.2f}" y1="{nyp:.2f}" '
                f'x2="{txp:.2f}" y2="{typ:.2f}" '
                f'stroke="{asp["color"]}" stroke-width="0.6" '
                f'opacity="{opacity}" fill="none"/>'
            )

    parts.append("</svg>")
    return "".join(parts)
