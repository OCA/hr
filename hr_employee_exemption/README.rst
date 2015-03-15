Employee Exemption
==================

This module implements employee exemption.
This allows in salary rules to know whether the employee is exempted from a source deduction.


Usage
=====

Go to: Human Resources -> Configuration -> Payroll -> Income Tax Exemptions
Create exemption types
exemple: 
 - name: 'Exemption from federal tax'
 - code: 'FED'

Go to: Human Resources -> Human Resources -> Employees
Select an employee
In the Tax Exemptions tab, add exemptions

In your salary rules, you may access check if an employee is exempted from a source deduction:
if employee.exempted_from('FED', payslip.date_from):
	result = ...
else:
	result = ...


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
