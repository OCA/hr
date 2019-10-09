.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=======================
HR Holidays Legal Leave
=======================

Allows the define which holiday type is to be considered legal/annual leave type.
Currently Odoo assumes by default leave type with limit=False. This is a problem if
you have more than one 'limited' leave type and specially confusing when trying to
set leaves from the employee form.

Installation
============

* clone the branch 10.0 of the repository https://github.com/OCA/hr
* add the path to this repository in your configuration (addons-path)
* update the module list
* search for "HR Holidays Legal Leave" in your addons
* install the module

Configuration
=============

To configure this module, you need to:

* assign legal leave type via ``Leaves > Configuration``:

  * choose Leave type you need
  * click ``[Edit]``
  * set **Legal/Annual** checkbox
  * click ``[Save]``


Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/116/10.0

Known issues / Roadmap
======================

By default, Odoo calculated leaves only by days, so there should be possible to calculate leaves by number of hours or to change the "number of days" field from integer to float.
There are a few cases that should improve the allocation requests:

* Each employee should have assigned to the contract a field about number of leaves negotiated, if different from the Legal Leave type number.
* For the first assignation the number of days should be calculated depending of the date of employment.
* Employees transfered between the same company Group should get the remaining days from previous company.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/hr/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback `here <https://github.com/OCA/
hr/issues/new?body=module:%20
hr_holidays_legal_leave%0Aversion:%20
8.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Salton Massally <smassally@idtlabs.sl>
* Fekete Mihai <feketemihai@gmail.com>
* Ivan Yelizariev <yelizariev@it-projects.info>
* Bassirou Ndaw <b.ndaw@ergobit.org>

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
