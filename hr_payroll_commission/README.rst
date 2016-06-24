.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=====================================
Payroll Commissions On Invoiced sales
=====================================

This module computes commissions on invoiced sales and allows you to add it to payslip

**Features list :**
    * Add commision rate, commission to contract.
    * Link commission to Payslip.

**For further information:**
    * Commissions management: http://open-net.ch/blog/la-comptabilite-salariale-suisse-avec-odoo-1/post/salaires-avec-odoo-commissions-et-notes-de-frais-78

**Remarks:**
    * As this module proposes its own report (same as the original, but with its own footer), don't forget to make it non-updatable.

Installation
============

Nothing special to install this module

Configuration
=============

Nothing special to configure this module

Usage
=====

    * To add commission to the payslip, you need to add a rate into the employee's contract. 

    .. image:: http://s16.postimg.org/iv10leobp/Screen_Shot_02_12_16_at_03_00_PM.png

    * You also need to add a the rule COMM to the contract.

    .. image:: http://s15.postimg.org/xa7roruij/Screen_Shot_02_12_16_at_02_58_PM.png

    * When you have this properly setup, you just have to compute your payslip to find COMM into the list.

    .. image:: http://s22.postimg.org/4ouwvh2f5/Screen_Shot_02_12_16_at_03_04_PM.png

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/hr/9.0

Known issues / Roadmap
======================

V1.0.0: 2014-11-07/dco
    * Module functions splitted from l10n_ch_hr_payroll.

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

* Sebastien Gendre <sge@open-net.ch>
* Yvon-Philippe Crittin <cyp@open-net.ch>
* David Coninckx <dco@open-net.ch>

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