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
[hr_contract_hourly_rate](hr_contract_hourly_rate/) | 1.0 | HR Contract Hourly Rate
[hr_contract_multi_jobs](hr_contract_multi_jobs/) | 1.0 | HR Contract Multi Jobs
[hr_contract_reference](hr_contract_reference/) | 1.0 | HR Contract Reference
[hr_employee_data_from_work_address](hr_employee_data_from_work_address/) | 1.0 | Update user's and partner's data fields from employee record
[hr_employee_firstname](hr_employee_firstname/) | 8.0.0.0.1 | Adds First Name to Employee
[hr_employee_legacy_id](hr_employee_legacy_id/) | 1.0 | Legacy Employee ID
[hr_employee_phone_extension](hr_employee_phone_extension/) | 1.0 | Employee Phone Extension
[hr_expense_account_period](hr_expense_account_period/) | 0.1 | Accounting period for HR expenses journal entries
[hr_expense_analytic_default](hr_expense_analytic_default/) | 0.1 | Manage default analytic account on expenses
[hr_expense_analytic_plans](hr_expense_analytic_plans/) | 1.0 | Use analytic plans in expenses
[hr_expense_invoice](hr_expense_invoice/) | 1.0 | Supplier invoices on HR expenses
[hr_expense_sequence](hr_expense_sequence/) | 1.0 | HR expense sequence
[hr_experience](hr_experience/) | 0.1 | Experience Management
[hr_family](hr_family/) | 1.0 | Employee Family Information
[hr_job_categories](hr_job_categories/) | 1.0 | HR Job Employee Categories
[hr_language](hr_language/) | 0.1 | Language Management
[hr_security](hr_security/) | 1.0 | HR Permission Groups
[hr_skill](hr_skill/) | 8.0.1.0.0 | Skill Management
[hr_webcam](hr_webcam/) | 1.0 | Capture employee picture with webcam

Unported addons
---------------
addon | version | summary
--- | --- | ---
[hr_accrual](__unported__/hr_accrual/) | 1.0 (unported) | Accrual
[hr_contract_init](__unported__/hr_contract_init/) | 1.0 (unported) | Contracts - Initial Settings
[hr_contract_state](__unported__/hr_contract_state/) | 1.0 (unported) | Manage Employee Contracts
[hr_department_sequence](__unported__/hr_department_sequence/) | 1.0 (unported) | Department Sequence
[hr_emergency_contact](__unported__/hr_emergency_contact/) | 1.0 (unported) | HR Emergency Contact
[hr_employee_education](__unported__/hr_employee_education/) | 1.0 (unported) | Employee Education Records
[hr_employee_id](__unported__/hr_employee_id/) | 1.0 (unported) | Employee ID
[hr_employee_seniority](__unported__/hr_employee_seniority/) | 1.0 (unported) | Employee Seniority
[hr_employee_state](__unported__/hr_employee_state/) | 1.0 (unported) | Employment Status
[hr_expense_sequence](__unported__/hr_expense_sequence/) | 0.1 (unported) | Adds a sequence on expenses
[hr_experience_analytic](__unported__/hr_experience_analytic/) | 0.1 (unported) | Experience and Analytic Accounting
[hr_holidays_extension](__unported__/hr_holidays_extension/) | 1.0 (unported) | HR Holidays Extension
[hr_infraction](__unported__/hr_infraction/) | 1.0 (unported) | Employee Infraction Management
[hr_job_hierarchy](__unported__/hr_job_hierarchy/) | 1.0 (unported) | Job Hierarchy
[hr_labour_recruitment](__unported__/hr_labour_recruitment/) | 1.0 (unported) | New Employee Recruitment and Personnel Requests
[hr_labour_union](__unported__/hr_labour_union/) | 1.0 (unported) | Labour Union
[hr_payroll_extension](__unported__/hr_payroll_extension/) | 1.0 (unported) | Payroll Extension
[hr_payroll_period](__unported__/hr_payroll_period/) | 1.0 (unported) | Payroll Period
[hr_payroll_register](__unported__/hr_payroll_register/) | 1.0 (unported) | Payroll Register
[hr_payroll_register_report](__unported__/hr_payroll_register_report/) | 1.0 (unported) | Payroll Register Report
[hr_payslip_amendment](__unported__/hr_payslip_amendment/) | 1.0 (unported) | Pay Slip Amendment
[hr_payslip_ytd_amount](__unported__/hr_payslip_ytd_amount/) | 1.0 (unported) | Payslip Year-to-date Amount
[hr_policy_absence](__unported__/hr_policy_absence/) | 1.0 (unported) | Absence Policy
[hr_policy_accrual](__unported__/hr_policy_accrual/) | 1.0 (unported) | Time Accrual Policy
[hr_policy_group](__unported__/hr_policy_group/) | 1.0 (unported) | Human Resources Policy Groups
[hr_policy_ot](__unported__/hr_policy_ot/) | 1.0 (unported) | Overtime Policy
[hr_policy_presence](__unported__/hr_policy_presence/) | 1.0 (unported) | Employee Presence Policy
[hr_public_holidays](__unported__/hr_public_holidays/) | 1.0 (unported) | Public Holidays
[hr_report_manpower](__unported__/hr_report_manpower/) | 1.0 (unported) | Man Power Report
[hr_report_payroll_attendance_summary](__unported__/hr_report_payroll_attendance_summary/) | 1.0 (unported) | Attendance Summary for Payroll
[hr_report_payroll_net](__unported__/hr_report_payroll_net/) | 1.0 (unported) | Net Payroll Payable
[hr_report_turnover](__unported__/hr_report_turnover/) | 1.0 (unported) | Employee Turn-over Report
[hr_resume](__unported__/hr_resume/) | 0.1 (unported) | Resume Management
[hr_salary_rule_variable](__unported__/hr_salary_rule_variable/) | 1.0 (unported) | Salary Rule Variables
[hr_schedule](__unported__/hr_schedule/) | 1.0 (unported) | Employee Shift Scheduling
[hr_simplify](__unported__/hr_simplify/) | 1.0 (unported) | Simplify Employee Records.
[hr_transfer](__unported__/hr_transfer/) | 1.0 (unported) | Departmental Transfer
[hr_wage_increment](__unported__/hr_wage_increment/) | 1.0 (unported) | HR Wage Increment
[hr_worked_days_activity](__unported__/hr_worked_days_activity/) | 1.0 (unported) | Worked Days Activity
[hr_worked_days_from_timesheet](__unported__/hr_worked_days_from_timesheet/) | 1.0 (unported) | Worked Days From Timesheet
[hr_worked_days_hourly_rate](__unported__/hr_worked_days_hourly_rate/) | 1.0 (unported) | Worked Days Hourly Rates

[//]: # (end addons)

Translation Status
------------------
[![Transifex Status](https://www.transifex.com/projects/p/OCA-hr-8-0/chart/image_png)](https://www.transifex.com/projects/p/OCA-hr-8-0)
