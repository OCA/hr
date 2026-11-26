On the contract form, the *Wage* box becomes a *Rate*: an amount and the
period it is quoted in.

Since hourly, daily, and weekly rates are not transformable to monthly
wage with precision, `wage` is being set to zero in these cases. An
extra `approximate_wage` field is added to store approximately computed
average monthly wage, using the number of work hours, days or weeks per
month set on the contract. It's also important to review payroll
calculation rules.

Writing `wage` directly keeps working: it stores a monthly amount.
Modules that write `wage` as a by-product and must not reset the rate can
pass `hr_contract_inverse_wage_skip` in the context.

When the module is installed on a database that already has contracts,
their current wage is kept as a monthly amount.

This module is based on different approach than
`hr_contract_hourly_rate` use.
