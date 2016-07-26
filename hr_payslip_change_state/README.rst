.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=========================
HR Payslip Change State
=========================

This module introduces the following features:
* This module allows to execute the actions that buttons inside a form do
    for many payslips at a time.
* The module checks if the required action is allowed for each payslip
* If any of the payslips are not in a suitable state a warning message will
pop up and no changes will be made
* If the action succeed a new tree view with the affected record will show

Installation
============

To install this module, you need to:

1.  Clone the branch 8.0 of the repository https://github.com/OCA/hr
2.  Add the path to this repository in your configuration (addons-path)
3.  Update the module list
4.  Go to menu *Setting -> Modules -> Local Modules*
5.  Search For *HR Payslip Change State*
6.  Install the module

It depends on hr_payroll_cancel. There is a pull request here:
https://github.com/OCA/hr/pull/248

Configuration
=============

No needed.

Usage
=====
1. Go to the payslip list view and select the ones you want to .
2. Unfold the "More" menu on the top and click on "Change state"
3. Select the action to execute

Credits
=======

Contributors
------------
* Aaron Henriquez <ahenriquez@eficent.com>
* Jordi Ballester <jordi.ballester@eficent.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.