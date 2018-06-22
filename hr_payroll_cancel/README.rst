.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
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
   :target: https://runbot.odoo-community.org/runbot/116/11.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/hr/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://odoo-community.org/logo.png>`_.

Contributors
------------
* Luis Torres (luis_t@vauxoo.com)
* Aaron Henriquez (ahenriquez@eficent.com)
* Lois Rilo (lois.rilo@eficent.com)
* Serpent Consulting Services Pvt. Ltd. <support@serpentcs.com>
* Duc, Dao Dong <duc.dd@komit-consulting.com> (https://komit-consulting.com)

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
