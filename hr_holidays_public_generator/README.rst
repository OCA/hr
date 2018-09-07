.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

===============================================
Hr Holidays Public Generator
===============================================

This module brings the shell for generating public holidays
based on year, country and state.

The module can not be used at its own and have to be extended.


Usage
=====

The module adds menu "Generate Public Holidays" under "Leaves/Public Holidays".
From this menu one can:
* generate public holidays for specific country (if there is no template set)
* copy public holidays for specific country

The module change the calculation of the leave days to exclude public holidays.

To extend the module one should
* create new module with name "hr_holidays_public_generator_<country code>"
* add hr_holidays_public_generator as dependency
* create wizard that inherit "hr.holidays.public.generator"
* implement copy public holidays function with name action_copy_%s_holidays
  where %s id the county code
* implement generate public holidays function with
  name action_generate_%s_holidays where %s id the county code


Known issues / Roadmap
======================

* The module does not handle half days leaves.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/hr/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Yu Weng <yweng@elegosoft.com>
* Nikolina Todorova <nikolina.todorova@initos.com>

Do not contact contributors directly about support or help with technical issues.

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
