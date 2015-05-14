Employee Exemption
==================

This module implements employee exemption.
This allows in salary rules to know whether the employee is exempted from a source deduction.


Usage
=====

Go to: Human Resources -> Configuration -> Payroll -> Income Tax Exemptions
Create an exemption (EX1)

Go to: Human Resources -> Configuration -> Payroll -> Salary Rules
Select a salary rule (R1) on which to apply the exemption
In the field 'Exemption', select the exemption EX1

Go to: Human Resources -> Human Resources -> Employees
Select an employee (E1)
In the Tax Exemptions tab, add exemption EX1 and the period of time over which it applies.

The amount will be 0 for rule R1 in employee E1's payslips.

Credits
=======

Contributors
------------
* David Dufresne <david.dufresne@savoirfairelinux.com>
* Maxime Chambreuil <maxime.chambreuil@savoirfairelinux.com>
* Pierre Lamarche <pierre.lamarche@savoirfairelinux.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
