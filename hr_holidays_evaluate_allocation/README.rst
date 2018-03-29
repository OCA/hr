.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==============================
Holidays Evaluation Allocation
==============================

This module allows you to define ruleset on leave type that are automatically
evaluated to get employee's leave allocation at any point in time

Installation
============

No additional steps necessary

Configuration
=============

To configure this module, you need to:

* Go to Human Resources > Configuration > Leaves Evaluation Ruleset
* Create Ruleset and save, then add your set of rules from the ruleset form
* Go to Leave types. choose a leave type with "Allow to Override limit" checkbox unchecked and select the ruleset you want evaluated for that rule type

Some important concepts to be understood whilst configuring rulesets are as follows:

Period Definition 
Defines the concept of leave period for this ruleset. For example, in the case of legal leaves
for some companies a leave period in the start of the year until the last day of that year during which
a leaves taken in that year accumulates and resets in the next.
Other companies use the anniversary of an employee's employment date to define leave period for that employee.
An example for each case is as follows...
Employee was hired on 2010-10-21
Start of Year - e.g of a leave period  2015-01-01 to 2015-12-31 - all leaves in this period are accumulated
Employment Anniversary -e.g. of a leave period - 2015-10-21 to 2016-10-20 - all leaves in this period are accumulated

Evaluation Mode
Defines what to do in cases wherein multiple rules satisfy a certain condition.
Options are as follows:
First - Consider the first rule that satisfies condition 
Minimum - Consider rule that evaluates to the least number of allocated days 
Maximum - Consider rule that evaluates to the most number of allocated days 

Rules
These are the individual lines that are evaluated in an order that depends on their sequence.
Rules with the smallest sequence number is evaluated first.

Rules are evaluated based on the following condition categories:

Always True - Will also be evaluated to true; an example of this is a case wherein your
organization offers Urgent Personal Leave that users can take at any time up to a certain amount.
In this case you can choose "Always True" and isnert the limit, e.g. "5" in the "Amount of Days" field

Range - Will evaluate a given field on the models, hr.employee, hr.contract, hr.job and test is the returned
value is within the range specified in Minimum Range an Maximum Range. 
be careful that this field returns and integer or float when computed
An example of this is allocating leaves based on employee's length of service.

Python Expression - Will evaluate a python expression. To ensure that your rule is aware of the date context
please use date_ref in place date.today() if you need to compare date against today()


Usage
=====

Once your ruleset and rules is configured using requesting for leaves is done as usual however leave allocations can not longer be done
as these are now computed from the ruleset attached to leave type

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/{repo_id}/{branch}

.. repo_id is available in https://github.com/OCA/maintainer-tools/blob/master/tools/repos_with_ids.txt
.. branch is "8.0" for example

Known issues / Roadmap
======================


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/
{project_repo}/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback `here <https://github.com/OCA/
{project_repo}/issues/new?body=module:%20
{module_name}%0Aversion:%20
{version}%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Salton Massally <smassally@idtlabs.sl>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.