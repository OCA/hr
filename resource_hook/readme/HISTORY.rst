11.0.1.0.0 (2019-05-28)
~~~~~~~~~~~~~~~~~~~~~~~

* Introduce hook in method '_get_work_days_data' of ResourceMixing class in
  order to allow changes in the logic to compute working hours within an
  interval. A new method '_get_work_hours' is now provided for this purpose.
  The method can be inherit to alter the standard behaviour.
