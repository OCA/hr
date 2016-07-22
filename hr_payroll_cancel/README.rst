.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

====================
HR Payroll Cancel
====================

This module introduces the following features:
* The module payroll_cancel allows the user to cancel a payslip whatever \
the previous state is.

Installation
============

To install this module, you need to:

1.  Clone the branch 8.0 of the repository https://github.com/OCA/hr
2.  Add the path to this repository in your configuration (addons-path)
3.  Update the module list
4.  Go to menu *Setting -> Modules -> Local Modules*
5.  Search For *HR Payroll Cancel*
6.  Install the module

Configuration
=============

No configuration needed

Usage
=====

Cancel a payslip
----------------
Go to: Human Resources -> Payroll -> Employee Payslip

- Choose a payslip from the list
- Click on the button "Cancel Payslip" to cancel the payslip
- Now the payslip is in rejected state

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/116/8.0

Known issues / Roadmap
======================

By default the Salary Journal should be set up with the field 'Check Date in
 Period' unflagged. Otherwise the application will raise an error message if
  the user enters a move date corresponding to a past period.


Credits
=======

Contributors
------------
* Jordi Ballester <jordi.ballester@eficent.com>
* OpenSynergy Indonesia <https://opensynergy-indonesia.com>

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