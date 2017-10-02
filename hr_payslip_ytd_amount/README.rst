Payslip Year-to-date Amount
===========================

This module implements a payslip model with a year-to-date amount column.
The slip is rendered in the employee's language.


Installation
============

 - Nothing to do except install the module


Configuration
=============

Translate the names of your salary rules that appear on payslips.
One way to do this is to create a .py file with the list of terms to translate.

example:

from openerp.tools.translate import _

[
	_('Gross Salary'),
	_('Net'),
	_('Income tax'),
]

Then the terms will appear in your pot file next time you generate it.


Usage
=====

Go to Human Resources -> Payroll -> Employee Payslips
Select the payslips you wish to generate, then click on Print -> Employee PaySlip (YTD Amount)

If you wish to translate the payslip in the employee's language, you need to assign him to a user.
Otherwise, the language of the user requesting the report will be used.


Known issues / Roadmap
======================
The header of the payslip generated is not translated.

Credits
=======

Contributors
------------

.. image:: http://sflx.ca/logo
   :alt: Savoir-faire Linux
   :target: http://sflx.ca

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