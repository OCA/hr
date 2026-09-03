# Copyright 2026 Forgeflow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
# The interpretation tables are module-level constants, so they are marked
# with _lt() and resolved later with env._()
# pylint: disable=W8161

from odoo.tools.translate import LazyTranslate

from .astro_calc import (
    PLANET_KEYS,
    SIGN_ELEMENTS,
    SIGN_MODALITIES,
    SIGN_POLARITIES,
    SIGN_SYMBOLS,
    SIGNS,
    get_house,
)

_lt = LazyTranslate(__name__)

SUN_INTERPRETATIONS = [
    # Aries
    (
        "Bold, pioneering and energetic. A natural leader with a competitive spirit "
        "and a strong drive to initiate new projects."
    ),
    # Taurus
    (
        "Reliable, patient and practical. Values stability, beauty and material "
        "comfort; known for persistence and sensuality."
    ),
    # Gemini
    (
        "Curious, adaptable and communicative. Quick-witted and versatile, with a "
        "constant need for intellectual stimulation."
    ),
    # Cancer
    (
        "Intuitive, nurturing and protective. Deeply empathetic and family-oriented, "
        "with a strong emotional memory."
    ),
    # Leo
    (
        "Confident, creative and generous. A natural performer who thrives in the "
        "spotlight; loyal and warm-hearted."
    ),
    # Virgo
    (
        "Analytical, diligent and precise. Pays close attention to detail and has a "
        "strong desire to be of service."
    ),
    # Libra
    (
        "Diplomatic, fair-minded and social. Seeks harmony and balance; values "
        "partnerships and aesthetic beauty."
    ),
    # Scorpio
    (
        "Intense, perceptive and determined. Possesses deep emotional power and a "
        "gift for transformation."
    ),
    # Sagittarius
    (
        "Optimistic, adventurous and philosophical. Loves freedom, travel and the "
        "pursuit of truth and knowledge."
    ),
    # Capricorn
    (
        "Disciplined, ambitious and responsible. Patient and strategic, with a strong "
        "drive for achievement."
    ),
    # Aquarius
    (
        "Original, idealistic and independent. A forward-thinking humanitarian who "
        "values friendship and innovation."
    ),
    # Pisces
    (
        "Compassionate, imaginative and intuitive. Deeply sensitive and spiritual, "
        "with a rich inner life."
    ),
]

MOON_INTERPRETATIONS = [
    # Aries
    (
        "Emotional reactions are quick and intense; needs independence and action "
        "to feel secure."
    ),
    # Taurus
    (
        "Seeks emotional security through stability, routine and physical comfort; "
        "very loyal once trust is established."
    ),
    # Gemini
    (
        "Processes emotions intellectually; needs communication and variety to feel "
        "at ease."
    ),
    # Cancer
    "Deeply intuitive and empathetic; home and family are the emotional anchor.",
    # Leo
    "Needs recognition and warmth; generous and loyal in emotional bonds.",
    # Virgo
    "Analytical about feelings; finds comfort in being useful and well-organised.",
    # Libra
    "Needs harmony and partnership; dislikes conflict and seeks emotional balance.",
    # Scorpio
    "Intense and private emotional world; deeply loyal but prone to jealousy.",
    # Sagittarius
    (
        "Needs freedom and optimism; enthusiastic but may avoid deeper emotional "
        "commitment."
    ),
    # Capricorn
    "Reserved with emotions; finds security through achievement and structure.",
    # Aquarius
    "Detached but humanitarian; connects best through shared ideas and ideals.",
    # Pisces
    ("Extremely sensitive and empathetic; absorbs surrounding emotions like a sponge."),
]

ASCENDANT_INTERPRETATIONS = [
    # Aries
    (
        "Projects energy, confidence and directness. First impression is dynamic "
        "and assertive."
    ),
    # Taurus
    (
        "Projects calm, reliability and groundedness. Others see you as steady "
        "and trustworthy."
    ),
    # Gemini
    (
        "Projects curiosity and adaptability. Others see you as lively, "
        "communicative and witty."
    ),
    # Cancer
    (
        "Projects sensitivity and nurturing. Others see you as caring, protective "
        "and approachable."
    ),
    # Leo
    (
        "Projects charisma and warmth. Others see you as confident, generous and "
        "magnetic."
    ),
    # Virgo
    (
        "Projects competence and modesty. Others see you as careful, helpful "
        "and analytical."
    ),
    # Libra
    (
        "Projects elegance and sociability. Others see you as charming, fair and "
        "refined."
    ),
    # Scorpio
    (
        "Projects intensity and mystery. Others see you as powerful, perceptive "
        "and magnetic."
    ),
    # Sagittarius
    (
        "Projects enthusiasm and openness. Others see you as adventurous, honest "
        "and optimistic."
    ),
    # Capricorn
    (
        "Projects authority and seriousness. Others see you as reliable, ambitious "
        "and disciplined."
    ),
    # Aquarius
    (
        "Projects originality and independence. Others see you as unique, friendly "
        "and intellectual."
    ),
    # Pisces
    (
        "Projects sensitivity and dreaminess. Others see you as gentle, empathetic "
        "and spiritual."
    ),
]

ELEMENT_DESCRIPTIONS = {
    "Fire": (
        "Your chart is dominated by "
        "<strong style='color:#e8554e'>Fire</strong> (♈♌♐). You tend "
        "to be enthusiastic, action-oriented and inspiring, with a strong creative "
        "drive and a natural optimism."
    ),
    "Earth": (
        "Your chart is dominated by "
        "<strong style='color:#7db87d'>Earth</strong> (♉♍♑). You tend "
        "to be practical, grounded and reliable, with a talent for building lasting "
        "results in the material world."
    ),
    "Air": (
        "Your chart is dominated by "
        "<strong style='color:#7ba7c7'>Air</strong> (♊♎♒). You tend to "
        "be intellectual, communicative and socially oriented, with a gift for "
        "connecting ideas and people."
    ),
    "Water": (
        "Your chart is dominated by "
        "<strong style='color:#9b7fc0'>Water</strong> (♋♏♓). You tend "
        "to be intuitive, empathetic and emotionally perceptive, with a deep inner "
        "life and strong instincts."
    ),
}

POLARITY_DESCRIPTIONS = {
    "Positive": (
        "Your chart leans towards <strong>Positive (Yang)</strong> signs "
        "(♈♊♌♎♐♒). You tend to be outwardly expressive, action-oriented "
        "and socially engaged."
    ),
    "Negative": (
        "Your chart leans towards <strong>Negative (Yin)</strong> signs "
        "(♉♋♍♏♑♓). You tend to be receptive, reflective and focused on "
        "inner depth and inner resources."
    ),
}

QUADRANT_DESCRIPTIONS = {
    "Q1": (
        "Many planets in the <strong>First Quadrant</strong> (Houses 1–3) "
        "suggest a strong focus on personal identity, self-expression and "
        "immediate environment."
    ),
    "Q2": (
        "Many planets in the <strong>Second Quadrant</strong> (Houses 4–6) "
        "suggest an emphasis on home, roots, daily routines and personal "
        "resources."
    ),
    "Q3": (
        "Many planets in the <strong>Third Quadrant</strong> (Houses 7–9) "
        "suggest a strong orientation towards relationships, partnerships "
        "and the pursuit of meaning."
    ),
    "Q4": (
        "Many planets in the <strong>Fourth Quadrant</strong> (Houses 10–12) "
        "suggest an emphasis on career, public life and collective or "
        "spiritual concerns."
    ),
}

MODALITY_DESCRIPTIONS = {
    "Cardinal": (
        "A strong <strong>Cardinal</strong> emphasis (♈♋♎♑) suggests you "
        "are a natural initiator who starts things, takes charge and drives change."
    ),
    "Fixed": (
        "A strong <strong>Fixed</strong> emphasis (♉♌♏♒) suggests you are "
        "persistent and determined, with the stamina to see things through and "
        "resist unnecessary change."
    ),
    "Mutable": (
        "A strong <strong>Mutable</strong> emphasis (♊♍♐♓) suggests you "
        "are adaptable and flexible, thriving in changing environments and "
        "bridging transitions with ease."
    ),
}


_ELEMENT_COLORS = {
    "Fire": "#e8554e",
    "Earth": "#7db87d",
    "Air": "#7ba7c7",
    "Water": "#9b7fc0",
}


def _dominant(counts):
    """Return the key with the highest count, or None if all equal."""
    if not counts:
        return None
    max_val = max(counts.values())
    if list(counts.values()).count(max_val) > 1:
        return None
    return max(counts, key=counts.get)


def build_interpretation(env, chart_data):
    """Return an HTML string interpreting the birth chart."""
    planets = chart_data["planets"]
    asc = chart_data.get("ascendant")

    from .astro_calc import lon_to_sign

    sun_i = lon_to_sign(planets["sun"])[0]
    moon_i = lon_to_sign(planets["moon"])[0]

    sections = []

    # ── Sun ──────────────────────────────────────────────────────────────────
    sections.append(
        f"<h6>☉ {env._('Sun')} in {SIGN_SYMBOLS[sun_i]} {env._(SIGNS[sun_i])}</h6>"
        f"<p>{env._(SUN_INTERPRETATIONS[sun_i])}</p>"
    )

    # ── Moon ─────────────────────────────────────────────────────────────────
    sections.append(
        f"<h6>☽ {env._('Moon')} in {SIGN_SYMBOLS[moon_i]} {env._(SIGNS[moon_i])}</h6>"
        f"<p>{env._(MOON_INTERPRETATIONS[moon_i])}</p>"
    )

    # ── Ascendant ─────────────────────────────────────────────────────────────
    if asc is not None:
        asc_i = lon_to_sign(asc)[0]
        asc_sign = f"{SIGN_SYMBOLS[asc_i]} {env._(SIGNS[asc_i])}"
        sections.append(
            f"<h6>AC {env._('Ascendant')} in {asc_sign}</h6>"
            f"<p>{env._(ASCENDANT_INTERPRETATIONS[asc_i])}</p>"
        )

    # ── Element, modality, polarity & quadrant distribution ──────────────────
    element_counts = {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0}
    modality_counts = {"Cardinal": 0, "Fixed": 0, "Mutable": 0}
    polarity_counts = {"Positive": 0, "Negative": 0}
    for key in PLANET_KEYS:
        sign_i = lon_to_sign(planets[key])[0]
        element_counts[SIGN_ELEMENTS[sign_i]] += 1
        modality_counts[SIGN_MODALITIES[sign_i]] += 1
        polarity_counts[SIGN_POLARITIES[sign_i]] += 1

    dominant_el = _dominant(element_counts)
    dominant_mod = _dominant(modality_counts)
    dominant_pol = _dominant(polarity_counts)

    dist_rows = "".join(
        f"<tr>"
        f"<td style='padding:2px 8px;color:{_ELEMENT_COLORS[el]}'>{env._(el)}</td>"
        f"<td style='padding:2px 8px'>"
        f"{'◉ ' * element_counts[el]}</td></tr>"
        for el in ("Fire", "Earth", "Air", "Water")
    )
    mod_rows = "".join(
        f"<tr><td style='padding:2px 8px'>{env._(mod)}</td>"
        f"<td style='padding:2px 8px'>"
        f"{'◉ ' * modality_counts[mod]}</td></tr>"
        for mod in ("Cardinal", "Fixed", "Mutable")
    )
    pol_rows = "".join(
        f"<tr><td style='padding:2px 8px'>{env._(pol)}</td>"
        f"<td style='padding:2px 8px'>"
        f"{'◉ ' * polarity_counts[pol]}</td></tr>"
        for pol in ("Positive", "Negative")
    )

    def _col(title, rows_html):
        return (
            f"<div>"
            f"<div class='text-muted fw-semibold' style='font-size:11px;"
            f"letter-spacing:.5px;margin-bottom:4px'>{title}</div>"
            f"<table style='font-size:12px'>{rows_html}</table>"
            f"</div>"
        )

    tables_html = (
        "<div style='display:flex;gap:24px;flex-wrap:wrap'>"
        + _col(env._("Elements"), dist_rows)
        + _col(env._("Modalities"), mod_rows)
        + _col(env._("Polarities"), pol_rows)
    )

    houses = chart_data.get("houses")
    dominant_quad = None
    if houses:
        quadrant_counts = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0}
        for key in PLANET_KEYS:
            h = get_house(planets[key], houses)
            if h:
                quadrant_counts[f"Q{(h - 1) // 3 + 1}"] += 1
        dominant_quad = _dominant(quadrant_counts)
        quad_labels = {
            "Q1": env._("Q1 (1–3)"),
            "Q2": env._("Q2 (4–6)"),
            "Q3": env._("Q3 (7–9)"),
            "Q4": env._("Q4 (10–12)"),
        }
        quad_rows = "".join(
            f"<tr><td style='padding:2px 8px'>{quad_labels[q]}</td>"
            f"<td style='padding:2px 8px'>"
            f"{'◉ ' * quadrant_counts[q]}</td></tr>"
            for q in ("Q1", "Q2", "Q3", "Q4")
        )
        tables_html += _col(env._("Quadrants"), quad_rows)

    tables_html += "</div>"

    dominant_texts = []
    if dominant_el:
        dominant_texts.append(f"<p>{env._(ELEMENT_DESCRIPTIONS[dominant_el])}</p>")
    if dominant_mod:
        dominant_texts.append(f"<p>{env._(MODALITY_DESCRIPTIONS[dominant_mod])}</p>")
    if dominant_pol:
        dominant_texts.append(f"<p>{env._(POLARITY_DESCRIPTIONS[dominant_pol])}</p>")
    if dominant_quad:
        dominant_texts.append(f"<p>{env._(QUADRANT_DESCRIPTIONS[dominant_quad])}</p>")

    sections.append(
        f"<h6>{env._('Chart Balance')}</h6>"
        + tables_html
        + ("<br>" + "".join(dominant_texts) if dominant_texts else "")
    )

    return "<div style='font-size:13px;line-height:1.6'>" + "".join(sections) + "</div>"


# Keys: (transiting_planet_key, aspect_name)
# {natal} is replaced at render time with the natal planet name.
TRANSIT_ASPECT_INTERPRETATIONS = {
    # ── Sun ──────────────────────────────────────────────────────────────────
    ("sun", "Conjunction"): _lt(
        "Solar energy illuminates and energises your natal {natal}. "
        "Awareness, vitality and intention peak in {natal}'s themes. "
        "This is a good moment to act consciously and decisively."
    ),
    ("sun", "Trine"): _lt(
        "Confidence and creative clarity flow harmoniously through your natal "
        "{natal}. Self-expression and initiative are well-supported right now."
    ),
    ("sun", "Sextile"): _lt(
        "Positive opportunities for self-expression arise around your natal "
        "{natal}. Vitality and initiative can be directed productively today."
    ),
    ("sun", "Square"): _lt(
        "Creative tension between your will and natal {natal} calls for "
        "conscious effort. Channel any friction into growth rather than conflict."
    ),
    ("sun", "Opposition"): _lt(
        "External circumstances or other people mirror your natal {natal} back "
        "to you. Objectivity and balance help you integrate the tension well."
    ),
    # ── Moon ─────────────────────────────────────────────────────────────────
    ("moon", "Conjunction"): _lt(
        "Emotional sensitivity peaks around your natal {natal}. Instincts and "
        "feelings are heightened, so trust your gut in {natal}'s domain today."
    ),
    ("moon", "Trine"): _lt(
        "Emotional harmony flows through your natal {natal}. Intuition and "
        "domestic life support {natal}'s natural expression right now."
    ),
    ("moon", "Sextile"): _lt(
        "Gentle emotional support nurtures your natal {natal}. "
        "Relationships and daily rhythms feel easy and comfortable."
    ),
    ("moon", "Square"): _lt(
        "Emotional tension or restlessness challenges your natal {natal}. "
        "Mood fluctuations are normal; patience and self-care help."
    ),
    ("moon", "Opposition"): _lt(
        "Emotional needs come into tension with your natal {natal}'s themes. "
        "Nurture yourself while staying open to others' perspectives."
    ),
    # ── Mercury ───────────────────────────────────────────────────────────────
    ("mercury", "Conjunction"): _lt(
        "Mercury sharpens thinking and communication around your natal {natal}. "
        "Ideas flow quickly; important conversations or decisions are highlighted."
    ),
    ("mercury", "Trine"): _lt(
        "Clear, harmonious thinking supports your natal {natal}. "
        "A good time for writing, negotiating or learning in {natal}'s areas."
    ),
    ("mercury", "Sextile"): _lt(
        "Mental opportunities arise around your natal {natal}. "
        "Communications and short-term plans tend to go smoothly today."
    ),
    ("mercury", "Square"): _lt(
        "Mental tension or miscommunication may surface around your natal "
        "{natal}. Double-check details and aim for clarity in all exchanges."
    ),
    ("mercury", "Opposition"): _lt(
        "Others' ideas challenge or stimulate your natal {natal}. "
        "Listen as much as you speak; different perspectives are valuable."
    ),
    # ── Venus ─────────────────────────────────────────────────────────────────
    ("venus", "Conjunction"): _lt(
        "Venus brings charm, harmony and pleasure to your natal {natal}. "
        "Social ease and aesthetic appreciation are highlighted today."
    ),
    ("venus", "Trine"): _lt(
        "Harmony and enjoyment flow easily around your natal {natal}. "
        "Relationships, beauty and creative pursuits are favoured."
    ),
    ("venus", "Sextile"): _lt(
        "Gentle social and creative opportunities arise around your natal "
        "{natal}. Diplomacy and warmth come naturally right now."
    ),
    ("venus", "Square"): _lt(
        "Indulgence or disharmony may challenge your natal {natal}. "
        "Balance pleasure with responsibility and avoid overcommitting."
    ),
    ("venus", "Opposition"): _lt(
        "Relationship tensions or differing values involve your natal {natal}. "
        "Seek balance between your own needs and those of others."
    ),
    # ── Mars ──────────────────────────────────────────────────────────────────
    ("mars", "Conjunction"): _lt(
        "Mars ignites your natal {natal} with drive and assertiveness. "
        "Energy and initiative peak, so act decisively but avoid impulsiveness."
    ),
    ("mars", "Trine"): _lt(
        "Energetic support flows easily to your natal {natal}. "
        "Physical vitality and motivation make this a good time for bold action."
    ),
    ("mars", "Sextile"): _lt(
        "A helpful burst of energy supports your natal {natal}. "
        "Courage and initiative are available for productive, targeted effort."
    ),
    ("mars", "Square"): _lt(
        "Friction and impatience challenge your natal {natal}. "
        "Avoid rash decisions; channel this intensity into constructive effort."
    ),
    ("mars", "Opposition"): _lt(
        "Competing drives or others' assertiveness challenge your natal {natal}. "
        "Seek compromise and direct your energy wisely to avoid confrontation."
    ),
    # ── Jupiter ───────────────────────────────────────────────────────────────
    ("jupiter", "Conjunction"): _lt(
        "A powerful surge of Jupiterian energy activates your natal {natal}. "
        "Opportunities for growth and abundance arise in {natal}'s themes."
    ),
    ("jupiter", "Trine"): _lt(
        "Fortunate energy flows easily to your natal {natal}. "
        "A period of natural growth, positive developments and deserved rewards."
    ),
    ("jupiter", "Sextile"): _lt(
        "Meaningful opportunities related to your natal {natal} come your way. "
        "Effort invested in {natal}'s themes now is likely to pay off well."
    ),
    ("jupiter", "Square"): _lt(
        "Tension between growth and limits challenges your natal {natal}. "
        "Overconfidence may need tempering; use this energy to overcome obstacles."
    ),
    ("jupiter", "Opposition"): _lt(
        "A need to balance expansion with reality around your natal {natal}. "
        "Others may bring opportunity or inflated expectations, so stay discerning."
    ),
    # ── Saturn ────────────────────────────────────────────────────────────────
    ("saturn", "Conjunction"): _lt(
        "Saturn's serious energy meets your natal {natal}. "
        "A period of testing and consolidation: structures built now are built to last."
    ),
    ("saturn", "Trine"): _lt(
        "Saturn supports your natal {natal} with stability and practical wisdom. "
        "A good time to formalise commitments or take disciplined, lasting action."
    ),
    ("saturn", "Sextile"): _lt(
        "Practical opportunities to strengthen your natal {natal}'s expression "
        "arise. Steady, responsible effort leads to tangible, lasting results."
    ),
    ("saturn", "Square"): _lt(
        "Saturn tests your natal {natal}, exposing weaknesses to be addressed. "
        "Challenges, met with patience, build resilience and long-term strength."
    ),
    ("saturn", "Opposition"): _lt(
        "External pressures or authority figures challenge your natal {natal}. "
        "Honest assessment and taking responsibility bring clarity and growth."
    ),
    # ── Uranus ────────────────────────────────────────────────────────────────
    ("uranus", "Conjunction"): _lt(
        "Sudden, liberating change disrupts your natal {natal}. "
        "Unexpected breakthroughs or upheavals shake up established patterns."
    ),
    ("uranus", "Trine"): _lt(
        "Exciting innovations and positive changes relate to your natal {natal}. "
        "Freedom, originality and new approaches are easily expressed now."
    ),
    ("uranus", "Sextile"): _lt(
        "Refreshing new ideas create positive shifts around your natal {natal}. "
        "Openness to change and flexibility bring real benefits at this time."
    ),
    ("uranus", "Square"): _lt(
        "Disruption and restlessness challenge your natal {natal}. "
        "The urge for radical change creates tension; avoid impulsive decisions."
    ),
    ("uranus", "Opposition"): _lt(
        "Unexpected events or people disrupt your natal {natal}. "
        "Adaptability and flexibility are essential to navigate these changes."
    ),
    # ── Neptune ───────────────────────────────────────────────────────────────
    ("neptune", "Conjunction"): _lt(
        "Neptune dissolves or spiritualises your natal {natal}. "
        "Intuition heightens, but confusion or idealisation is also possible."
    ),
    ("neptune", "Trine"): _lt(
        "Spiritual sensitivity and creative inspiration flow gently through "
        "your natal {natal}. Intuition and empathy are naturally heightened."
    ),
    ("neptune", "Sextile"): _lt(
        "Subtle spiritual or creative opportunities emerge around your natal "
        "{natal}. Dreams and intuition offer useful, gentle guidance now."
    ),
    ("neptune", "Square"): _lt(
        "Confusion or idealisation may cloud your natal {natal}'s expression. "
        "Be wary of self-deception and keep yourself grounded in clear facts."
    ),
    ("neptune", "Opposition"): _lt(
        "Illusions or escapism challenge your natal {natal}. "
        "Grounding and discernment are essential; reality may need reassessing."
    ),
    # ── Pluto ─────────────────────────────────────────────────────────────────
    ("pluto", "Conjunction"): _lt(
        "Profound, irreversible transformation touches your natal {natal}. "
        "Old patterns are stripped away to reveal deeper power and authentic truth."
    ),
    ("pluto", "Trine"): _lt(
        "Deep, empowering change flows smoothly through your natal {natal}. "
        "Transformation feels purposeful and ultimately regenerative."
    ),
    ("pluto", "Sextile"): _lt(
        "An opportunity for deep personal growth around your natal {natal} "
        "arises. Subtle but meaningful transformation is available if embraced."
    ),
    ("pluto", "Square"): _lt(
        "Intense power struggles or compulsive forces challenge your natal "
        "{natal}. Resistance amplifies pressure; embrace the necessary change."
    ),
    ("pluto", "Opposition"): _lt(
        "External forces of change confront your natal {natal}. "
        "Old structures may collapse; rebirth comes through letting go."
    ),
}


def build_transit_interpretation(env, natal_data, transit_data, aspects, today):
    """Return (aspects_html, interpretations_html) for the transit chart.

    aspects_html — date header + active aspects table (goes in the side column).
    interpretations_html — per-aspect interpretation texts (goes full-width below).
    """
    from .astro_calc import (
        ASPECT_LABELS,
        PLANET_KEYS,
        PLANET_NAMES,
        PLANET_SYMBOLS,
        SIGN_SYMBOLS,
        SIGNS,
        lon_to_sign,
    )

    planets_t = transit_data["planets"]

    date_str = today.strftime("%B %d, %Y")
    date_header = (
        f"<p class='text-muted mb-2' style='font-size:11px'>"
        f"{env._('Transits for')} <strong>{date_str}</strong> "
        f"{env._('compared to natal chart')}</p>"
    )

    tight = sorted([a for a in aspects if a["orb"] <= 8], key=lambda a: a["orb"])[:12]

    if not tight:
        no_aspects = f"<p>{env._('No major aspects currently active.')}</p>"
        return (
            "<div style='font-size:13px;line-height:1.6'>"
            + date_header
            + no_aspects
            + "</div>",
            "",
        )

    rows_html = ""
    interp_html = ""
    for asp in tight:
        ti = PLANET_KEYS.index(asp["transit_key"])
        ni = PLANET_KEYS.index(asp["natal_key"])
        t_sym = PLANET_SYMBOLS[ti]
        n_sym = PLANET_SYMBOLS[ni]
        t_name = env._(PLANET_NAMES[ti])
        n_name = env._(PLANET_NAMES[ni])
        t_sign_i = lon_to_sign(planets_t[asp["transit_key"]])[0]
        rows_html += (
            f"<tr>"
            f"<td style='padding:2px 6px' title='{t_name}'>"
            f"<span style='font-size:15px'>{t_sym}</span></td>"
            f"<td style='padding:2px 4px;font-size:12px'>"
            f"{SIGN_SYMBOLS[t_sign_i]}&nbsp;{env._(SIGNS[t_sign_i])}</td>"
            f"<td style='padding:2px 6px;font-size:15px;color:{asp['color']}'>"
            f"{asp['symbol']}</td>"
            f"<td style='padding:2px 4px;font-size:12px;color:{asp['color']}'>"
            f"{env._(asp['aspect'])}</td>"
            f"<td style='padding:2px 6px' title='{n_name}'>"
            f"<span style='font-size:15px'>{n_sym}</span></td>"
            f"<td style='padding:2px 6px;font-size:11px' class='text-muted'>"
            f"{asp['orb']}°</td>"
            f"</tr>"
        )
        key = (asp["transit_key"], asp["aspect"])
        text = TRANSIT_ASPECT_INTERPRETATIONS.get(key, "")
        if text and asp["orb"] <= 6:
            filled = env._(text).format(natal=n_name)
            aspect_label = env._(ASPECT_LABELS[asp["aspect"]]).lower()
            aspect_colored = f"<span style='color:{asp['color']}'>{aspect_label}</span>"
            heading = env._(
                "Transiting %(transit)s forms a %(aspect)s with your natal %(natal)s",
                transit=t_name,
                aspect=aspect_colored,
                natal=n_name,
            )
            interp_html += (
                f"<h6>"
                f"<span style='color:{asp['color']}'>"
                f"{t_sym} {asp['symbol']} {n_sym}</span>"
                f" {heading}"
                f"<span class='text-muted' style='font-size:10px;"
                f"font-weight:normal;margin-left:4px'>{asp['orb']}°</span>"
                f"</h6>"
                f"<p>{filled}</p>"
            )

    aspects_table = (
        f"<h6 class='mt-2'>{env._('Active Aspects (Transit → Natal)')}</h6>"
        "<table style='font-size:12px'>"
        "<thead><tr class='text-muted' style='font-size:11px'>"
        f"<th style='padding:2px 6px'>{env._('Transit')}</th>"
        f"<th style='padding:2px 4px'>{env._('In Sign')}</th>"
        f"<th style='padding:2px 6px' colspan='2'>{env._('Aspect')}</th>"
        f"<th style='padding:2px 6px'>{env._('Natal')}</th>"
        f"<th style='padding:2px 6px'>{env._('Orb')}</th>"
        f"</tr></thead><tbody>{rows_html}</tbody></table>"
    )
    aspects_html = (
        "<div style='font-size:13px;line-height:1.6'>"
        + date_header
        + aspects_table
        + "</div>"
    )
    interp_out = (
        (
            "<div style='font-size:13px;line-height:1.6'>"
            f"<h5 class='text-info mt-1 mb-2'>{env._('Transit Interpretations')}</h5>"
            + interp_html
            + "</div>"
        )
        if interp_html
        else ""
    )
    return aspects_html, interp_out


def build_daily_horoscope(env, aspects):
    """Return a one-or-two sentence horoscope for today, as plain text.

    Picks the tightest transit aspect that has an interpretation text, so the
    result is short enough to fit in a web client notification. Returns an
    empty string when no transit is close enough to comment on.
    """
    from .astro_calc import (
        ASPECT_LABELS,
        PLANET_KEYS,
        PLANET_NAMES,
        PLANET_SYMBOLS,
    )

    for asp in sorted((a for a in aspects if a["orb"] <= 6), key=lambda a: a["orb"]):
        text = TRANSIT_ASPECT_INTERPRETATIONS.get((asp["transit_key"], asp["aspect"]))
        if not text:
            continue
        ti = PLANET_KEYS.index(asp["transit_key"])
        ni = PLANET_KEYS.index(asp["natal_key"])
        n_name = env._(PLANET_NAMES[ni])
        # Same msgid as the profile interpretation, so both share a translation
        heading = env._(
            "Transiting %(transit)s forms a %(aspect)s with your natal %(natal)s",
            transit=env._(PLANET_NAMES[ti]),
            aspect=env._(ASPECT_LABELS[asp["aspect"]]).lower(),
            natal=n_name,
        )
        return (
            f"{PLANET_SYMBOLS[ti]} {asp['symbol']} {PLANET_SYMBOLS[ni]} "
            f"{heading}. {env._(text).format(natal=n_name)}"
        )
    return ""
