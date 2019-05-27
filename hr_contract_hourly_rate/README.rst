.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

HR Contract Hourly Rate
=======================

This module was written to extend the functionality of employees contracts
to support hourly rates between dates in calculation of the wage.

Note: This module also modifies options in selection of wage calculation,
"wage" to "yearly",
"hourly_rate" to "hourly",
and adds "monthly" option. Modules that are dependants of this module should
take in consideration this change when calculating the wage.

Installation
============

To install this module, you need to:

* clone the branch 8.0 of the repository https://github.com/OCA/hr
* add the path to this repository in your configuration (addons-path)
* update the module list
* search for "HR Contract Hourly Rate" in your addons
* install the module

Usage
=====

The module depends on hr_contract_multi_job module, and extends it so you
can set hourly wages on the jobs assigned to the contract. The wage can be
set between certain dates.

Credits
=======

Contributors
------------

* David Dufresne <david.dufresne@savoirfairelinux.com>
* Pierre Lamarche <pierre.lamarche@savoirfairelinux.com>
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
