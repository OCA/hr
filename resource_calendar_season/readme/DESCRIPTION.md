This module lets a single working time (`resource.calendar`) behave differently
depending on the time of the year, using **recurring** seasons defined by month,
so they repeat automatically every year.

A *seasonal* calendar holds no working hours of its own. For each date it
delegates the working-time computation to the calendar of the season that
matches that date, falling back to a configurable default working time for any
date not covered by a season.