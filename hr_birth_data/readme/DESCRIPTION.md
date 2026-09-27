Adds birth time and birth coordinates to the employee profile.

Provides the base fields used by astrological and other birth-data
modules:

-  **Birth Time** (``birth_hour``): decimal hours, e.g. 14.5 = 14:30
-  **Birth Time Known** (``birth_hour_known``): tells a birth at midnight
   apart from an unknown time, which a float column alone cannot do. Any
   time other than 00:00 ticks it automatically
-  **Birth Latitude / Longitude**: geographic coordinates of the birth
   place

These fields are displayed in the *Private Information* tab of the
employee form, alongside the existing *Place of Birth* field.

This module contains no calculations — it is a data layer intended to be
extended by modules such as ``hr_birth_astral_chart``.
