This module ensures a consistent working times history when using the
**hr_contract** and **hr_employee_calendar_planning** modules together.

There are 3 different data models which can relate to working time
(resource.calendar) records:

* Employees (hr.employee)
* Contracts (hr.contract)
* Resources (resource.resource) -> related to hr.employee through resource.mixin

The **hr_employee_calendar_planning** module adds the calendar_ids field
to employees, which allows a more flexible working times configuration:
Instead of selecting a single resource.calendar, multiple calendars can be
combined into one auto-generated calendar.

However, contracts are not considered when creating auto-generated calendars.
This can lead to unexpected behaviour, because the active contract calendar
and the employee calendar can diverge (calendar mismatch). Additionally, when
configuring a new contract, or changing the existing contract calendar,
the employee calendar will be overwritten by the contract calendar.

To resolve this issue, this module migrates current and previous contract
calendars into the calendar_ids and thus the auto-generated calendar.
Additionally, changes to the employee calendar by contracts are prevented.
The resource_calendar_id field is hidden in contract views, since all
working times should be managed in the calendar_ids field for each employee.
However, it is still possible to keep a meaningful contract history,
e.g. for salary information.
