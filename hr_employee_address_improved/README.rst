.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

============================
HR Employee Address Improved
============================

When the HR modules are enabled and we have 1 employee for each users,
some parts of the UI become confusing because
we have several partners for the same person:

    1. res.user inherits from res.partner,
       and fields such as the email are stored in there

    2. hr.employee has address_id and address_home_id.
       The first one refers to the work address
       (presumably the partner related to the company of the address
       of an office of the company, so not a problem)
       but the other one is the home address
       and if used it will probably be linked to a partner
       with the same name as the employee.

Assumption: we would like to exclude home addresses
from the list of available partners in m2o and m2m fields.

.. note::

    when this module is installed a post init hook
    **will set all partners related via `address_home_id` as inactive**.

Installation
============

To install this module, you need to:

* clone the branch 10.0 of the repository https://github.com/OCA/hr
* add the path to this repository in your configuration (addons-path)
* update the module list
* search for "HR Employee Address Improved" in your addons
* install the module

Configuration
=============

No extra configuration needed.


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

* Simone Orsi <simone.orsi@camptocamp.com>
* Alexandre Fayolle <alexandre.fayolle@camptocamp.com>

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
