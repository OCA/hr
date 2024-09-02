This module is a template for building on top of. It _will_ need glue modules to
work with various other modules. Most notably, ``hr_holidays`` will not work
without modification.

The module may need improvements for timezone handling; this is currently
untested. ``_split_into_weeks`` splits weeks on the timezone of the datetime
objects passed to it instead of on the timezone of the calendar. The calculation
of the current week number uses ``fields.Date.today()`` instead of the
environment's or calendar's timezone. Finally, child calendars may have a
different timezone compared to their parent, which is probably not a desired
feature.

This module assumes that a week always starts on a Monday. Upstream Odoo appears
to do the same, but this may not be desired by certain audiences.
