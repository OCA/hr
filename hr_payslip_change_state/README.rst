=============================
HR Payslip Change State
=============================

This module introduces the following features:
* This module allows change the state of many payslips form the
tree view
* The module checks if the require state is allowed for each payslip
* If any of the payslips are not in a suitable state a warning message will
pop up and no changes will be made

Installation
============

It depends on hr_payroll_cancel. There is a pull request here:
https://github.com/OCA/hr/pull/247

Configuration
=============

No needed.

Usage
=====
1. Go to the payslip list and select the ones you want to cancel.
2. Unfold the "More" menu on the top
3. Select the required state
4. To complete the request, click on "Execute" button.