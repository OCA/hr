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

Employees have no access to `hr.employee`, which Odoo reserves for HR users, so
they reach their own chart through **Employees > My Astral Chart** instead. That
view is read-only and strictly personal: the chart fields on `res.users` are
only filled for the user asking for them, since a sun sign would otherwise give
away a colleague's birth date.

Astronomical calculations use `pyswisseph` (Python binding for Swiss Ephemeris)
for high-precision planetary positions.

The birth time is read as local clock time at the birth place, while the
ephemeris works in Universal Time. The timezone is derived from the birth
coordinates with `timezonefinder`, and the rules in force on the birth date are
applied, historical daylight saving included. Without coordinates the country of
birth is used instead, but only when every timezone that country uses was on the
same UTC offset that day, so the offset is never a guess.

The Ascendant and the houses need real coordinates, since they depend on where
on Earth the birth happened, not only when. With a resolvable time but no
coordinates the planets are exact and the Ascendant is left unknown; with no
resolvable time the chart falls back to noon UT, which still places the slow
bodies correctly.
