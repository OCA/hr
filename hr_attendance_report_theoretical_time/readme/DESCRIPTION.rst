This module adds a new report called "Theoretical vs Attended Time Analysis"
that compares worked time, measured through attendances records, with the
theoretical time, computed from employee's working calendar, public holidays
and employee specific leaves. Missing attendance days are generated on the fly
in the report with their corresponding theoretical hours.

There is the possibility of counting as theoretical time some leave types if
specified in them.

As an example, imagine a work week with 40 theoretical hours, and these
attendance situation:

* Monday: Worked 10 hours
* Tuesday: Worked 10 hours
* Wednesday: Worked 10 hours
* Thursday: Worked 10 hours
* Friday: Ask for a compensation leave (said leave type), as already worked
  40 hours.

On the report, whole week should put 40 theoretical hours - 8 per day - against
40 worked hours (although they were on previous days, and none on Friday).

On contrary, if you want to take a holiday one of that days, you should ask for
a leave type without the check for counting as theoretical time, and then the
whole week will be 32 theoretical hours against the worked hours of that week
without the leave.
