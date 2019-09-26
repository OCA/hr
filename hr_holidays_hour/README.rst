.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

=========================
Leave Management in hours
=========================

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
If the "Working Time" is not set for the employee, but the employee has a contract with
a working schedule, the duration (in hours) will be automatically filled as well.

Usage
=====

To request a leave, an employee can:

#. From menu Leaves, create a Leave Request by setting the duration in hours (instead of days)

To allocate hours for an employee:

#. From menu Leaves, create an Allocation Request by setting the duration in hours (instead of days)

To fully benefit from this module, the HR Officer should set a working time schedule for the employees.
The duration (in hours) will be automatically filled while setting the start and the end date of a leave.
In thi cas, the employee requesting a leave is still able to adjust the hours manually.

To set a working schedule for an employee:

#. From menu Employees -> Employees, select one employee
#. Set the "Working Time" field

If the "Working Time" is not set for the employee, but the employee has a contract with
a working schedule, the duration (in hours) will be automatically filled as well.

#. From menu Employees -> Employees, select one employee
#. Click on Contracts and select the employee's actual contract
#. Set the "Working Schedule" field


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/116/10.0


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/hr/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Tests for `resource_calendar` are repeated from the Odoo SA standard module `resource`.

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Antonio Esposito <a.esposito@onestein.nl>
* Andrea Stirpe <a.stirpe@onestein.nl>

Do not contact contributors directly about support or help with technical issues.

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
