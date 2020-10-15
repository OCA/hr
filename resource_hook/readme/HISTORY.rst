11.0.1.0.0 (2019-05-28)
~~~~~~~~~~~~~~~~~~~~~~~

* Introduce hook in method `_get_work_days_data` of ResourceMixing class in
  order to allow changes in the logic to compute working hours within an
  interval. A new method `_get_work_hours` is now provided for this purpose.
  The method can be inherit to alter the standard behaviour.

12.0.1.0.2 (2020-06-09)
~~~~~~~~~~~~~~~~~~~~~~~

* Introduce hook in method `get_work_hours_count` of ResourceCalendar class in
  order to allow changes in the logic to compute working hours within an
  interval. A new method `_get_work_hours` is now provided for this purpose.
  The method can be inherit to alter the standard behaviour.


13.0.1.0.0 (2020-09-29)
~~~~~~~~~~~~~~~~~~~~~~~

* Introduce hook in methods `list_work_time_per_day` and `list_leaves` of
  ResourceMixing class in order to allow changes in the logic to compute
  working hours within an interval.

* Introduce hook in methods `_get_days_data`, `_get_resources_day_total`,
  `get_work_hours_count`, `plan_hours` and `_compute_hours_per_day` of
  ResourceCalendar class in order to allow changes in the logic to compute
  working hours within an interval or an attendance. A new method
  `_get_work_hours_attendance` is now provided for this purpose.
  The method can be inherit to alter the standard behaviour.
