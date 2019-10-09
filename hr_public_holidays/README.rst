.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==================
HR Public Holidays
==================

This module allows to define public holidays at country or state level by year.

These holidays will be taken into account in standard resource allocation and
requests, and can be used by other modules as base data.

As well, this module will try to highlight known holidays in calendar views.

Configuration
=============

#. Go to *Leaves > Public Holidays > Public Holidays*.
#. Create a record, specifying:

   * Year for the holidays you are going to set.
   * Optionally, a country where the holidays apply. If not set, it means
     holidays are global.
#. On "Public Holidays" section, introduce a line for each of the holidays
   you want to specify.
#. Optionally, you can set at line level several countries for limiting the
   holidays to that countries.

On following years, you can speed up public holidays creation using a wizard:

#. Go to *Leaves > Public Holidays > Create Next Year Public Holidays*.
#. If there's no special situation, you only need to click on "Create" for
   applying the same holidays as this year for the next.
#. If you need to generate holidays for another year different from next one,
   or take as source another year different from the last one, go to the
   "Optional" page for configuring these parameters.

To customize the color to highlight public holidays in calendar views:

#. navigate to *Settings > Technical > System parameters*
#. provide a value to `calendar.public_holidays_color` key (both hex RGB and
   valid web color names will do, and invalid color settings would be ignored
   completely).

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/116/10.0

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

* Michael Telahun Makonnen <mmakonnen@gmail.com>
* Fekete Mihai <feketemihai@gmail.com>
* Nikolina Todorova <nikolina.todorova@initos.com>
* Alexis de Lattre <alexis.delattre@akretion.com>
* Salton Massally (iDT Labs) <smassally@idtlabs.sl>
* Ivan Yelizariev <yelizariev@it-projects.info>
* Bassirou Ndaw <b.ndaw@ergobit.org>
* Tecnativa - Pedro M. Baeza
* Nedas Zilinskas <nedas.zilinskas@xpansa.com> (Ventor, Xpansa Group <https://ventor.tech/>)
* Artem Kostyuk <a.kostyuk@mobilunity.com>

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
