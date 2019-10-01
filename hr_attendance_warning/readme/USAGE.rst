Two new columns are added to resource.calendar.attendances, margin_from and
margin_to. This two fields indicate the margin an employee has to check in
and check out. If an employee enters at 9:00 with a margin of 30 minutes,
it is expected to enter between 8:30 and 9:30, otherwise a warning will be
generated.

Different warnings created to a single employee the same day are stacked as
lines in a hr.attendance.warning object. From there you can check employee's
attendances to check the reason of the warning and correct the issues.

After that, click on the Solve button to mark the warning as resolved.