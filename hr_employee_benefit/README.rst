Employee Benefit
================

This module implements employee benefits in order to produce payslips.

Employee benefits can be computed automatically at a specific point in a payroll structure.
They can also be computed using the button on the payslip form, in the 'Employee Benefits' tab.

Also, they can be added manually on a payslip.

If a benefit has 2 different rates in the same payslip period,
the 2 rates will be weighted by the fraction of the payslip over which they apply.


Configuration
=============

Setting employee benefits
-------------------------
Go to Human Resources -> Configuration -> Payroll -> Employee Benefit Categories
Create your own employee benefit.
Select the salary rules over which the benefit will be summed.
Add as many different rates as needed.

On the contract of an employee, add employee benefits.
Select the category of benefit, the rate and dates between which the benefit will be activated.

Setting the payroll structure
-----------------------------
In a salary rule of your payroll structure, you may call

payslip.compute_benefits(payslip)

This allows compute the employee benefits at a specific point in the
payroll structure.

Whithin a salary rule, you may sum of benefits for a list of category codes:

 - Employee contribution:
    result = rule.sum_benefits(payslip, codes=['A1', 'B2'])

 - Employer contribution:
    result = rule.sum_benefits(payslip, codes=['C3'], employer=True)

The parameter codes is the list of benefit categories to include.
To sum over the benefits related to the current salary rule:

 - Employee contribution:
    result = rule.sum_benefits(payslip)

 - Employer contribution:
    result = rule.sum_benefits(payslip, employer=True)

If the salary rule is related to no benefit categories, the method will sum
all benefit categories.


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
