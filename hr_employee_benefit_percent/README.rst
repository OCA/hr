Employee Benefit Percent
========================
Add employee benefits based on a percent of the gross salary


Configuration
=============

When setting your employee benefits, you may select the type 'Percent of Gross Salary'.
If you write 2.5 in the employee/employer amount field, this means 2.5 % of the gross salary.

If you use this feature, you must ensure that the field gross_salary on the payslip is filled
before the employee benefits are computed.

For this, you may add the following code in the proper salary rule:

payslip.set_gross_salary(payslip, GROSS)

where 'GROSS' is the code of the salary rule that defines the gross salary.


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
