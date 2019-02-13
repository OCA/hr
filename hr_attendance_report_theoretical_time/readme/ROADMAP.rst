* Employees with less than 1 week in the company will show full week
  theoretical hours.
* Activate ORM cache for improving performance on computing theoretical hours,
  but assuring that the cache is cleared when the conditions of the computation
  changes.
* If you change employee's working time, theoretical hours for non attended
  days will be computed according this new calendar. You have to define
  start and end dates inside the calendar for avoiding this side effect.
* Theoretical hours of affected days when changing the leave type to be
  included or not in theoretical time are not recomputed.
