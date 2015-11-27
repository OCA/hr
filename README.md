[![Runbot Status](https://runbot.odoo-community.org/runbot/badge/flat/116/8.0.svg)](https://runbot.odoo-community.org/runbot/repo/github-com-oca-hr-116)
[![Build Status](https://travis-ci.org/OCA/hr.svg?branch=8.0)](https://travis-ci.org/OCA/hr)
[![Coverage Status](https://coveralls.io/repos/OCA/hr/badge.png?branch=8.0)](https://coveralls.io/r/OCA/hr?branch=8.0)
[![Code Climate](https://codeclimate.com/github/OCA/hr/badges/gpa.svg)](https://codeclimate.com/github/OCA/hr)

Human Resources
===============

Odoo modules related to Human Resources.

Dependencies
------------

The following modules require `report_aeroo` from [lp:aeroo](https://launchpad.net/aeroo)

* `hr_payroll_register_report`
* `hr_report_manpower`
* `hr_report_payroll_attendance_summary`
* `hr_report_payroll_net`
* `hr_report_turnover`

[//]: # (addons)
Available addons
----------------
addon | version | summary
--- | --- | ---
[hr_contract_default_trial_length](hr_contract_default_trial_length/) | 8.0.1.0.0 | Define default trail length for contracts
[hr_contract_hourly_rate](hr_contract_hourly_rate/) | 8.0.1.0.0 | HR Contract Hourly Rate
[hr_contract_multi_jobs](hr_contract_multi_jobs/) | 8.0.1.0.0 | HR Contract Multi Jobs
[hr_contract_reference](hr_contract_reference/) | 8.0.1.0.0 | HR Contract Reference
[hr_department_sequence](hr_department_sequence/) | 1.0 | Add sequence on department
[hr_employee_age](hr_employee_age/) | 8.0.1.0.0 | Age field for employee
[hr_employee_benefit](hr_employee_benefit/) | 8.0.1.0.0 | Employee Benefit
[hr_employee_data_from_work_address](hr_employee_data_from_work_address/) | 8.0.1.0.0 | Update user's and partner's data fields from employee record
[hr_employee_firstname](hr_employee_firstname/) | 8.0.0.0.2 | Adds First Name to Employee
[hr_employee_gravatar](hr_employee_gravatar/) | 8.0.1.0.0 | Employees Synchronize Gravatar image
[hr_employee_legacy_id](hr_employee_legacy_id/) | 8.0.1.0.0 | Legacy Employee ID
[hr_employee_phone_extension](hr_employee_phone_extension/) | 8.0.1.0.0 | Employee Phone Extension
[hr_expense_account_period](hr_expense_account_period/) | 8.0.0.1.0 | Accounting period for HR expenses journal entries
[hr_expense_analytic_default](hr_expense_analytic_default/) | 8.0.0.1.0 | Manage default analytic account on expenses
[hr_expense_analytic_plans](hr_expense_analytic_plans/) | 8.0.1.0.0 | Use analytic plans in expenses
[hr_expense_invoice](hr_expense_invoice/) | 8.0.1.0.0 | Supplier invoices on HR expenses
[hr_expense_sequence](hr_expense_sequence/) | 8.0.1.0.0 | HR expense sequence
[hr_experience](hr_experience/) | 8.0.0.1.0 | Experience Management
[hr_family](hr_family/) | 8.0.1.2.0 | Employee Family Information
[hr_job_categories](hr_job_categories/) | 8.0.1.0.0 | HR Job Employee Categories
[hr_language](hr_language/) | 8.0.0.1.0 | Language Management
[hr_recruitment_partner](hr_recruitment_partner/) | 8.0.1.0.0 | Automatically create a Partner for Applicants
[hr_salary_rule_reference](hr_salary_rule_reference/) | 8.0.1.0.0 | Salary Rule Reference
[hr_security](hr_security/) | 8.0.1.0.0 | HR Permission Groups
[hr_skill](hr_skill/) | 8.0.1.1.0 | Skill Management
[hr_webcam](hr_webcam/) | 8.0.1.0.0 | Capture employee picture with webcam

Unported addons
---------------
addon | version | summary
--- | --- | ---
[hr_accrual](hr_accrual/) | 1.0 (unported) | Accrual
[hr_contract_init](hr_contract_init/) | 1.0 (unported) | Contracts - Initial Settings
[hr_contract_state](hr_contract_state/) | 1.0 (unported) | Manage Employee Contracts
[hr_emergency_contact](hr_emergency_contact/) | 1.0 (unported) | HR Emergency Contact
[hr_employee_education](hr_employee_education/) | 1.0 (unported) | Employee Education Records
[hr_employee_id](hr_employee_id/) | 1.0 (unported) | Employee ID
[hr_employee_seniority](hr_employee_seniority/) | 1.0 (unported) | Employee Seniority
[hr_employee_state](hr_employee_state/) | 1.0 (unported) | Employment Status
[hr_experience_analytic](hr_experience_analytic/) | 0.1 (unported) | Experience and Analytic Accounting
[hr_holidays_extension](hr_holidays_extension/) | 1.0 (unported) | HR Holidays Extension
[hr_infraction](hr_infraction/) | 1.0 (unported) | Employee Infraction Management
[hr_job_hierarchy](hr_job_hierarchy/) | 1.0 (unported) | Job Hierarchy
[hr_labour_recruitment](hr_labour_recruitment/) | 1.0 (unported) | New Employee Recruitment and Personnel Requests
[hr_labour_union](hr_labour_union/) | 1.0 (unported) | Labour Union
[hr_payroll_extension](hr_payroll_extension/) | 1.0 (unported) | Payroll Extension
[hr_payroll_period](hr_payroll_period/) | 1.0 (unported) | Payroll Period
[hr_payroll_register](hr_payroll_register/) | 1.0 (unported) | Payroll Register
[hr_payroll_register_report](hr_payroll_register_report/) | 1.0 (unported) | Payroll Register Report
[hr_payslip_amendment](hr_payslip_amendment/) | 1.0 (unported) | Pay Slip Amendment
[hr_payslip_ytd_amount](hr_payslip_ytd_amount/) | 1.0 (unported) | Payslip Year-to-date Amount
[hr_policy_absence](hr_policy_absence/) | 1.0 (unported) | Absence Policy
[hr_policy_accrual](hr_policy_accrual/) | 1.0 (unported) | Time Accrual Policy
[hr_policy_group](hr_policy_group/) | 1.0 (unported) | Human Resources Policy Groups
[hr_policy_ot](hr_policy_ot/) | 1.0 (unported) | Overtime Policy
[hr_policy_presence](hr_policy_presence/) | 1.0 (unported) | Employee Presence Policy
[hr_public_holidays](hr_public_holidays/) | 1.0 (unported) | Public Holidays
[hr_report_manpower](hr_report_manpower/) | 1.0 (unported) | Man Power Report
[hr_report_payroll_attendance_summary](hr_report_payroll_attendance_summary/) | 1.0 (unported) | Attendance Summary for Payroll
[hr_report_payroll_net](hr_report_payroll_net/) | 1.0 (unported) | Net Payroll Payable
[hr_report_turnover](hr_report_turnover/) | 1.0 (unported) | Employee Turn-over Report
[hr_resume](hr_resume/) | 0.1 (unported) | Resume Management
[hr_salary_rule_variable](hr_salary_rule_variable/) | 1.0 (unported) | Salary Rule Variables
[hr_schedule](hr_schedule/) | 1.0 (unported) | Employee Shift Scheduling
[hr_simplify](hr_simplify/) | 1.0 (unported) | Simplify Employee Records.
[hr_transfer](hr_transfer/) | 1.0 (unported) | Departmental Transfer
[hr_wage_increment](hr_wage_increment/) | 1.0 (unported) | HR Wage Increment
[hr_worked_days_activity](hr_worked_days_activity/) | 1.0 (unported) | Worked Days Activity
[hr_worked_days_from_timesheet](hr_worked_days_from_timesheet/) | 1.0 (unported) | Worked Days From Timesheet
[hr_worked_days_hourly_rate](hr_worked_days_hourly_rate/) | 1.0 (unported) | Worked Days Hourly Rates

[//]: # (end addons)

Translation Status
------------------
[![Transifex Status](https://www.transifex.com/projects/p/OCA-hr-8-0/chart/image_png)](https://www.transifex.com/projects/p/OCA-hr-8-0)
