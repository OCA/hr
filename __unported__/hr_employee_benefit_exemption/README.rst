Employee Benefit Exemption
==========================

Add exemptions on employee benefit categories.


Usage
=====

Go to: Human Resources -> Configuration -> Payroll -> Income Tax Exemptions
Create an exemption (EX1)

Go to: Human Resources -> Configuration -> Payroll -> Salary Rules
Select a salary rule (R1) on which to apply the exemption
In the field 'Exemption', select the exemption EX1

Go to Human Resources -> Configuration -> Payroll -> Employee Benefit Categories
Create a benefit category (B1). In the 'Exemptions' tab, add exemption EX1.

In the python code of the salary rule R1, calling the following function will exclude all benefits related to B1:

    result = rule.sum_benefits(payslip)


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
