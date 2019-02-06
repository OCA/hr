In Odoo 12.0, `_leave_intervals()` returns `Intervals` which is a list of
tuples (start_timestamp, end_timestamp, `resource.calendar.leaves` record).
Since this module does not operate with `resource.calendar.leaves`, it's
setting third component of a tuple to a `hr.holidays.public.line` record.
This may or may not be a problem, yet since this component is also being set to
`resource.calendar.attendance` records in `_attendance_intervals()`, seems it
should be ok.
