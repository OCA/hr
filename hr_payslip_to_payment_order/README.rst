.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

========================
Payslip To Payment Order
========================

This module adds feature to: 

1. Create payment order easily from payslip.
2. Monitor payslip payment progress

Installation
============

To install this module, you need to:

1.  Clone the branch 8.0 of the repository https://github.com/OCA/hr
2.  Add the path to this repository in your configuration (addons-path)
3.  Update the module list
4.  Go to menu *Setting -> Modules -> Local Modules*
5.  Search For *Payslip To Payment Order*
6.  Install the module

Usage
=====

Monitor On Progress Payslip's Payment
-------------------------------------

1. Go to *Human Resources -> Payslip -> Payslip To Payment Order*
2. Activate *Unpaid* and *Partial* filter

Create Payment Order From Payslip
---------------------------------

1. Go to *Human Resources -> Payslip -> Payslip To Payment Order*
2. Activate *Unpaid* and *Partial* filter
3. Select payslip data that you want to pay
4. Click *More* button
5. Click *Create Payment Order From Payslip* button
6. Select *Company* (for multi-company environment)
7. Choose Bank/Cash payment
8. Choose Bank (if you select Bank on step 7)
9. Choose *Payment Mode*
10. Click *Create* button

Note:

Odoo will not automatically open payment order after user click *Create*
button. This due possibility user do not have authority to view/edit payment order.
Payment order then can be editted/processed through it's own menu under Accounting
app.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/116/8.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/hr/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Andhitia Rama <andhitia.r@gmail.com>

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
