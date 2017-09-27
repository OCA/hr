.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

====================================
Set supplier invoices on HR expenses
====================================

This module should be used when a supplier invoice is paid by an employee. It
allows to set a supplier invoice for each expense line, adding the
corresponding journal items to transfer the debt to the employee.


Installation
============

Install the module the regular way.

Configuration
=============

You don't need to configure anything more to use this module.

Usage
=====

* Create an expense sheet.
* Add an expense line to sheet with an invoice_id selected or create one new.
* Process expense sheet.
* On paying expense sheet, you are reconciling supplier invoice too.

Known issues / Roadmap
======================

* Multiple payment terms for a supplier invoice are not handled correctly.
* Partial reconcile supplier invoices are also not correctly handled.

Credits
=======

Contributors
------------

* Pedro M. Baeza <pedro.baeza@tecnativa.com>
* Vicent Cubells <vicent.cubells@tecnativa.com>

Icon
----

* Thanks to https://openclipart.org/detail/201137/primary%20template%20invoice
* Thanks to https://openclipart.org/detail/15193/Arrow%20set%20%28Comic%29
* Original hr_expense icon

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
