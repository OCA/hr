Since hourly, daily, and weekly rates are not tranformable to monthly wage with
precision, ``wage`` is being set to zero in these cases. An extra ``approximate_wage``
field is added to store approximately computed average monthly wage. It's also
important to review payroll calculation rules.

This module is based on different approach than ``hr_contract_hourly_rate`` use.
