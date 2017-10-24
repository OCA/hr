.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

Spouse for employee
======================

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

Roadmap
=======
* Support poligamy
* Forbade the deletion of the spouse tag, it is now forcecreate so on updates
  will reappear if deleted.


Contributors
------------

* Giovanni Francesco Capalbo <giovanni@therp.nl>
* Holger Brunn <hbrunn@therp.nl>

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
