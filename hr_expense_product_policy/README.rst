.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=========================
HR Expense Product Policy
=========================

This module add feature to set up policy regarding product on expense. Product
policy that ruled by this module are:

1. Force use of product on Expense
2. Allowed product that can be used based on employee's department
3. Allowed product that can be used based on employee's job
4. Allowed product that can be used based on employee himself

Installation
============

To install this module, you need to:

1.  Clone the branch 8.0 of the repository https://github.com/OCA/hr
2.  Add the path to this repository in your configuration (addons-path)
3.  Update the module list
4.  Go to menu *Setting -> Modules -> Local Modules*
5.  Search For *HR Expense Product Policy*
6.  Install the module

Configuration
=============

**Force Product Usage**
To force product usage on expense, you need to:

1. Open employee data
2. Open *HR Setting* tab
3. Activate *Required Expense Product*

Hint:
You can use mass editing module to apply this rule

**Department's Expense Product Policy**
To set up department's allowed product policy based on product category, you need to:

1. Open department data
2. Select product category on *Allowed Expense Product Category*

To set up department's allowed product policy based on specific product, you need to:

1. Open department data
2. Select product on *Allowed Expense Product*

Note:
* Only product with *Can be expense* flag turn on can be used, even if that product belong to category specified on *Allowed Expense Product Category*
* Only product with *Can be expense* flag turn on can be selected on *Allowed Expense Product*
* Final result of allowed product can be seen on *All Allowed Expense Products*

**Job's Expense Product Policy**
To set up job's allowed product policy based on product category, you need to:

1. Open job data
2. Select product category on *Allowed Expense Product Category*

To set up job's allowed product policy based on specific product, you need to:

1. Open job data
2. Select product on *Allowed Expense Product*

Note:
* Only product with *Can be expense* flag turn on can be used, even if that product belong to category specified on *Allowed Expense Product Category*
* Only product with *Can be expense* flag turn on can be selected on *Allowed Expense Product*
* Final result of allowed product can be seen on *All Allowed Expense Products*

**Employee's Expense Product Policy**
To set up employee's allowed product policy based on product category, you need to:

1. Open employee data
2. Select product category on *Allowed Expense Product Category*

To set up employee's allowed product policy based on specific product, you need to:

1. Open employee data
2. Select product on *Allowed Expense Product*

To activate product policy, you need to:

1. Activate *Limit Product Selection*

Note:
* Only product with *Can be expense* flag turn on can be used, even if that product belong to category specified on *Allowed Expense Product Category*
* Only product with *Can be expense* flag turn on can be selected on *Allowed Expense Product*
* Final result of allowed product can be seen on *All Allowed Expense Products*. The list will be the aggregation of (1) department's product policy, (2) job's product policy, and (3) employee's product policy


Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/116/8.0


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/hr/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed `feedback
<https://github.com/OCA/
hr/issues/new?body=module:%20
hr_expense_expense_product_policy%0Aversion:%20
8.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Michael Viriyananda <viriyananda.michael@gmail.com>
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
