.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

HR Simplify Employee Records
============================

This module was written to extend the functionality of employees,
employees contracts and job positions to support:

    1. Make the job id in employee object reference job id in latest contract.
    2. When moving from employee to contract pre-populate the employee field.
    3. In the contract form show only those positions belonging to the
       department the employee belongs to.
    4. Make official identification number unique.

Installation
============

To install this module, you need to:

* clone the branch 8.0 of the repository https://github.com/OCA/hr
* add the path to this repository in your configuration (addons-path)
* update the module list
* search for "HR Simplify Employee Records" in your addons
* install the module

Usage
=====



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
