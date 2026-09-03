View your full Western astrological birth chart directly from your employee profile.

Depends on `hr_birth_data` for the birth time and coordinates fields.

Adds an **Astral Chart** tab to the employee form showing:

- **Sun Sign**, **Moon Sign** and **Ascendant** summary badges
- An SVG zodiac wheel with planetary positions
- A detailed table with degree, minute, sign and house for each planet
  (Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto,
  Chiron, Black Moon Lilith, Ceres)
- Astrological houses (Whole Sign system) when birth time and location are provided
- Current transits biwheel and interpretation
- An optional daily horoscope notification, shown once a day when you open Odoo

Astronomical calculations use `pyswisseph` (Python binding for Swiss Ephemeris)
for high-precision planetary positions.
