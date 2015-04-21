.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

HR Contract Reference
=====================

This module was written to extend the functionality of employees contracts
to support sequence of contract reference which will be generated
automatically from the sequence predefined.

Installation
============

To install this module, you need to:

* clone the branch 8.0 of the repository https://github.com/OCA/hr
* add the path to this repository in your configuration (addons-path)
* update the module list
* search for "HR Contract Reference" in your addons
* install the module

Configuration
=============

If you want to modify the format of the sequence, go to
Seetings -> Technical -> Sequences & Identifiers -> Sequences
and search for the "Contract Reference" sequence, where you modify
it's prefix and numbering formats.

Usage
=====

When you will create a new employee contract, the field reference will be
assigned automatically with the next number of the predefined sequence.

Credits
=======

Contributors
------------

* Michael Telahun Makonnen <mmakonnen@gmail.com>
* Fekete Mihai <feketemihai@gmail.com>

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
