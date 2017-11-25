.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: https://www.gnu.org/licenses/agpl
    :alt: License AGPL-3

===================
Spouse for employee
===================

Module adds a field where you can specify the spouse. It also checks that two
employees do not have the same spouse. A spouse is a partner.
Spouse partners have a label that designates them as such.

Usage
=====

The "spouse" tag will be unmodifiable from the partner form. it is managed by
editing the spouse selection on HR employee. The error messages when you try to
delete such tag are verbose.
So if I try to delete or add the spouse tag from res partner A, i will receive a
message: " A is the spouse of B, go on HR employee B Spouse field to change it".

Known issues / Roadmap
======================

* Support poligamy
* Forbade the deletion of the spouse tag, it is now forcecreate so on updates
  will reappear if deleted.


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/hr/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/hr/issues/new?body=module:%20hr_employee_spouse%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Giovanni Francesco Capalbo (Therp) <giovanni@therp.nl>
* Holger Brunn (Therp) <hbrunn@therp.nl>

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
