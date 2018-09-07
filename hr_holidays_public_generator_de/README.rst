.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

===============================================
Hr Holidays Public Generator DE
===============================================

This module extends the hr_holidays_public_generator module
and implements the functionality needed to generate and copy
the public holidays in Germany.


Usage
=====

Go to "Leaves/Public Holidays/Generate Public Holidays"
* Choose "Year" for which the public holidays will be generated
* Choose "Germany" in the "Country" dropdown
* "State" field
    ** Choose "State" if you want the holidays only for specific state
    ** Leave "State" empty if you want all public holidays
* "From Template" field
    ** Choose "From Template". This will be used as template and
all holidays with field "Date may change" = False (static holidays),
will be copied.
All floating holidays ("Date may change" = True ), will be calculated
for the relevant "Year"
* press "Generate" button


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
