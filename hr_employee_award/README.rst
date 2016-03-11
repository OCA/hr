.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==========================
Employee Awards Management
==========================

This module adds functionality to manage awards to your
employees

Installation
============

To install this module, you need to:

1.  Clone the branch 8.0 of the repository https://github.com/OCA/hr
2.  Add the path to this repository in your configuration (addons-path)
3.  Update the module list
4.  Go to menu *Setting -> Modules -> Local Modules*
5.  Search For *Employee Awards Management*
6.  Install the module

Configuration
=============


Usage
=====

To use this module, you need to:

+**To see your award datas, you need to:**
 +
 +1. Got to menu *Human Resources -> Human Resources -> Employee*
 +2. Open your employee data
 +3. Infraction data will be shown on *Awards*

**To see employee awards data(s), you need to:**

1. Go to menu *Human Resources -> Awards -> Awards*

Note:
* You have to be a member on *Human Resources / Officer* to see all employee award datas


**To create award, you need to:**

1. Go to menu *Human Resources -> Awards -> Awards*

Note:
* To create award user has to belong to *Human Resources / Officer* group

**To confirm award, you need to:**

1. Go to menu *Human Resources -> Awards -> Awards*
2. Open an award that has *draft* status
3. Make sure all entries are correct
4. Click *Confirm* button

Note:
* To confirm award user has to belong to *Human Resources / Officer* group

**To approve award, you need to:**

1. Go to menu *Human Resources -> Awards -> Awards*
2. Open an award that has *confirmed* status
3. Click *Approve* button

Note:
* To approve award user has to belong to *Human Resources / Manager* group

**To issued  award, you need to:**

1. Go to menu *Human Resources -> Awards -> Awards*
2. Open an award that has *Approved* status
3. Click *Issue* button

Note:
* To execute award user has to belong to *Human Resources / Manager* group

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/116/8.0

Known issues / Roadmap
======================


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/hr/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed `feedback
<https://github.com/OCA/
hr/issues/new?body=module:%20
hr_employee_awards%0Aversion:%20
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
