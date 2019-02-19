You need to be at least "Attendance / Manual Attendance" for being able to see
the attendances report.

For including some leave types in the theoretical time, you have to:

#. Go to *Leaves > Configuration > Leave Types*.
#. Select leave type you want to include.
#. Check the mark "Include in theoretical hours".

When generating non worked days, this module uses a start date for beginning
the series generation, which is:

* Manual start date set on the employee.
* If not set, the greatest of these 2 dates:

  * Employee creation date.
  * Working calendar line start date.

For configuring manual start date, you have to:

#. Go to *Employees > Employees*.
#. Select an employee.
#. Go to "HR Settings" page.
#. Set the date in "Theoretical hours start date" field.

The generation will stop on the end date of the working calendar line or today,
so don't forget to properly set start and end dates of the lines of the working
calendar for not leaving empty spaces between them.
