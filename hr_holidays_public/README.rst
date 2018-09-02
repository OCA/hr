.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

==================
HR Public Holidays
==================

This module is a technical module to handle public holidays.
The calculation of each leave can exclude rest days or public holiday.
The calculation of each leave includes the number of hours taken from 
.employee calendar attendances

Installation
============

To install this module, you need to:

* clone the branch 11.0 of the repository https://github.com/OCA/hr
* add the path to this repository in your configuration (addons-path)
* update the module list
* search for "Public Holidays" in your addons
* install the module

Configuration
=============

Go to Leaves -> Configuration and open a Leave Type

* Check "Exclude Rest Days" to exclude resource calendar rest days
* Check "Exclude Public Holidays" to exclude public holidays
* Uncheck "Compute Full Days" to allow fractional days.

Usage
=====

Go to the menu *Leaves > Public Holidays > Public Holidays* and create your
public holidays.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/116/11.0

Known issues / Roadmap
======================


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

* Odoo Community Association: `Icon <https://odoo-community.org/logo.png>`_.


Contributors
------------

* Michael Telahun Makonnen <mmakonnen@gmail.com>
* Fekete Mihai <feketemihai@gmail.com>
* Nikolina Todorova <nikolina.todorova@initos.com>
* Alexis de Lattre <alexis.delattre@akretion.com>
* Salton Massally (iDT Labs) <smassally@idtlabs.sl>
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
