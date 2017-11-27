.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License

===========================
Employee Family Information
===========================

This module allows you to enter extra information about employee's family.
Module  adds a field where you can specify the spouse. It also checks that two
employees do not have the same spouse. A spouse is a partner.
Spouse partners have a label that designates them as such.
Also the fixed selection in 'Marital status' on employee is replaced by a
configurable selection.

Configuration
=============

To configure marital statuses, you need to:

#. go to `Human Resources/Settings/Marital statuses` to edit marital statuses


Usage
=====

To use this module, you need to go to any employee form, and look for the
*Family* tab. You will be able to enter family information there.
The "spouse" tag will be unmodifiable from the partner form. It is managed by
editing the spouse selection on HR employee. The error messages when you try to
delete such tag are verbose.
So if I try to delete or add the spouse tag from res partner A, I will receive a
message: " A is the spouse of B, go on HR employee B Spouse field to change it".

For further information, please visit:

 * https://www.odoo.com/forum/help-1

Known issues / Roadmap
======================

* Remove all birthdate fields (spouse, children, parents) and incorporate
  them in their partners by adding dependency partner_contact_birthdate
  and write migration script + views.

Credits
=======

Contributors
------------

* Michael Telahun Makonnen <mmakonnen@gmail.com>
* Sébastien Alix <sebastien.alix@osiell.com>
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
