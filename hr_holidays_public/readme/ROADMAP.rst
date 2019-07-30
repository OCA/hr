In Odoo 12.0, `_leave_intervals()` returns `Intervals` which is a list of
tuples (start_timestamp, end_timestamp, `resource.calendar.leaves` record).
Since this module does not operate with `resource.calendar.leaves`, it's
setting third component of a tuple to a `hr.holidays.public.line` record.
This may or may not be a problem, yet since this component is also being set to
`resource.calendar.attendance` records in `_attendance_intervals()`, seems it
should be ok.

There are no restrictions to block users from modifying or removing calendar
events linked to public holidays. There's a suggestion to overload `write` and
`unlink` methods of `calendar.event`, but it might have other impacts like
users not being able to edit event tags, or even custom fields.

Regional public holidays are shown in the public calendar. The regions will be
noted in the description of the event, but it'll be shown to all users. It'd
be good to have it show only for users in these regions.
