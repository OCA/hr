This module allows you to get warnings when there are
inconsistencies between the theoric check in time of an employee
and what has happened.

Every time there is a check_in or a check_out the module checks whether
it is inside the employee's working time or not and creates a warning if it's
not.

It also testes the opposite case, an employee not coming to work at expected
time. A cron is executed every 5 minutes checking resource.calendar.attendances
and checks if every employee related to it has done what it was expected.

The module also adds a systray icon to receive notifications about warnings,
which can be disabled by setting show_attendance_warning system parameter to
false.
