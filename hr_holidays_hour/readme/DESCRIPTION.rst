The standard Odoo application "Leave Management" allows employees to create
leave allocations and requests by defining their duration in days.

By installing this module, the duration of the leaves will be expressed in hours,
instead of days. In the leave form, a new field "duration" (in hours) will be displayed
and the original field "duration" (in days) will be hidden.

As an example, let's say that a working day for an employee is 8 hours:

* 1 day = 8 hours
* 2 days = 16 hours
* 0.5 days (half day) = 4 hours
* 0.125 days = 1 hour

etc...

If the employee wants to request a leave of one hour:

* with the standard Odoo app "Leave Management" the employee would write 0.125 days
* with module "hr_holidays_hour" installed, the employee writes 1.0 hour

If the employee wants to request half a day:

* with the standard Odoo app "Leave Management" the employee would write 0.5 days
* with module "hr_holidays_hour" installed, the employee writes 4.0 hours


In case a working time schedule is defined for an employee, the duration (in hours) will be
automatically filled while setting the starting date and the ending date of a leave request.
