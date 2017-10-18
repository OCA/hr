.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===============================
Employee Identification Numbers
===============================

Company wide unique employee ID. Supports:

* Random ID Generation
* Sequence

This module supports sequence of employee ID which will be generated
automatically from the sequence predefined.

Nevertheless, if you need a difference ID in particular cases
you can pass a custom value for `identification_id`: if you do it
no automatic generation happens.

Installation
============

To install this module, you need to:

* clone the branch 10.0 of the repository https://github.com/OCA/hr
* add the path to this repository in your configuration (addons-path)
* update the module list
* search for "Employee Identification Numbers" in your addons
* install the module

Configuration
=============

If you want to modify the format of the sequence, go to
Settings -> Technical -> Sequences & Identifiers -> Sequences
and search for the "Employee ID" sequence, where you modify
its prefix and numbering formats.

To configure the 'ID Generation Method', the '# of Digits' and
the 'Sequence', activate the developer mode and go to
Employees -> Configuration -> Employee ID.


Usage
=====

When you will create a new employee, the field reference will be
assigned automatically with the next number of the predefined sequence.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/116/10.0

Known issues / Roadmap
======================

* When installing the module, the ID of existing employees is not generated automatically

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/hr/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Michael Telahun Makonnen <mmakonnen@gmail.com>
* Adrien Peiffer (ACSONE) <adrien.peiffer@acsone.eu>
* Salton Massally (iDT Labs) <smassally@idtlabs.sl>
* Andhitia Rama (OpenSynergy Indonesia) <andhitia.r@gmail.com>
* Simone Orsi <simone.orsi@camptocamp.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
