.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=================
HR Payroll Cancel
=================

This module allows the user to cancel a payslip whatever the previous state is
without doing a refund. When the user cancel the journal entry is deleted
and  the payslip state is set to rejected. Then the user is able to set the
state to draft again and later on he/she is able to confirm again the payslip.

If there’s a refund for a payslip the user should not cancel the entry because
the refund would still be confirm. In that case, the user have either to
confirm again the payslip or cancel the refund.

Usage
=====

Go to: Payroll -> Employee Payslip

#. Choose a payslip from the list.
#. Click on the button "Cancel Payslip" to cancel the payslip.
#. Now the payslip is in rejected state.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/116/9.0

Credits
=======

Contributors
------------
* Luis Torres (luis_t@vauxoo.com)
* Aaron Henriquez (ahenriquez@eficent.com)
* Lois Rilo (lois.rilo@eficent.com)

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
