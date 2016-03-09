.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

========================
HR Infraction Management
========================

This module add employee infraction management

Installation
============

To install this module, you need to:

1.  Clone the branch 8.0 of the repository https://github.com/OCA/hr
2.  Add the path to this repository in your configuration (addons-path)
3.  Update the module list
4.  Go to menu *Setting -> Modules -> Local Modules*
5.  Search For *HR Infraction Management*
6.  Install the module

Configuration
=============

To configure this module, you need to:

**Configure Infraction Category**

1. Go to menu *Human Resources -> Configuration -> Infraction Category*

**Configure Infraction Warning**

1. Go to menu *Human Resources -> Configuration -> Infraction Warning*

Usage
=====

**To see your infraction data, you need to:**

1. Got to menu *Human Resources -> Human Resources -> Employee*
2. Open your employee data
3. Infraction data will be shown on *Diciplinary Information*


**To see your subordinate infraction infraction data(s), you need to:**

1. Go to menu *Human Resources -> Infraction -> Infractions*

Note:
* You have to be a member on *Infraction Management / User* to see your subordinate data 


**To create infraction document, you need to:**

1. Go to menu *Human Resources -> Infraction -> Infractions*

Note:
* To create infraction document user has to belong to *Infraction Management / User* or *Infraction Management / Officer* group
* User who belong to *Infraction Management / User* can only create infraction document for his/her subordinate 
* User who belong to *Infraction Management / Officer* can create infraction document for all employee

**To confirm infraction document, you need to:**

1. Go to menu *Human Resources -> Infraction -> Infractions*
2. Open an infraction document that has *draft* state
3. Make sure all entries are correct
4. Click *Confirm* button

Note:
* To confirm infraction document user has to belong to *Infraction Management / User* or *Infraction Management / Officer* group
* User who belong to *Infraction Management / User* can only confirm infraction document for his/her subordinate 
* User who belong to *Infraction Management / Officer* can confirm infraction document for all employee

**To approve infraction document, you need to:**

1. Go to menu *Human Resources -> Infraction -> Infractions*
2. Open an infraction document that has *confirmed*
3. Fill (1) *Category*, and (2) *Warning*
4. Click *Approve* button

Note:
* To approve infraction document user has to belong to *Infraction Management / Officer* group

**To execute infraction document, you need to:**

1. Go to menu *Human Resources -> Infraction -> Infractions*
2. Open an infraction document that has *Approved*
3. Make sure (1) *Category*, and (2) *Warning* is correct. You still can edit both fields.
4. Click *Valid* button

Note:
* To execute infraction document user has to belong to *Infraction Management / Manager* group

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/116/8.0

Known issues / Roadmap
======================

* This module does not inted to execute any action related to infraction (e.g. demotion, transfer to other department, etc)
* Incompatible data model when migrated from 7.0
* No revision mecanism avalaible

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/hr/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed `feedback
<https://github.com/OCA/
hr/issues/new?body=module:%20
hr_infraction%0Aversion:%20
8.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Andhitia Rama <andhitia.r@gmail.com>

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
