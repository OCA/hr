.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License

Set supplier invoices on HR expenses
====================================

This module should be used when a supplier invoice is paid by an employee. It
allows to set  a supplier invoice for each expense line, adding the
corresponding journal items to transfer the debt to the employee.


Installation
============

Install the module the regular way.

Configuration
=============

You don't need to configure anything more to use this module.

Usage
=====

Instead of coding a full expense line, select an existing supplier invoice,
and then the rest of the fields will be auto-filled and grayed.

When you generate the expenses account entries, lines with invoices filled
will be generated as opposite of the payable move line of the invoice, and
both will be reconciled, letting the employee payable account as the only
open balance.

Known issues / Roadmap
======================

* Multiple payment terms for a supplier invoice are not handled correctly.
* Partial reconcile supplier invoices are also not correctly handled.

Credits
=======

Contributors
------------

* Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>

Icon
----

* Thanks to https://openclipart.org/detail/201137/primary%20template%20invoice
* Thanks to https://openclipart.org/detail/15193/Arrow%20set%20%28Comic%29
* Original hr_expense icon

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
