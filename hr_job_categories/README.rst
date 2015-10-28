.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

HR Job Employee Categories
==========================

This module was written to extend the functionality of jobs
to support tagging employees based on their job positions.
For example, all Supervisors could be attached to the Supervisors category.
Define which categories a job belongs to in the configuration for the job.
When an employee is assigned a particular job the categories attached to that
job will be attached to the employee record as well.

Installation
============

To install this module, you need to:

* clone the branch 8.0 of the repository https://github.com/OCA/hr
* add the path to this repository in your configuration (addons-path)
* update the module list
* search for "HR Job Employee Categories" in your addons
* install the module

Usage
=====

Just like on Employee form, you can select Tags on every Job form view.
Once a contract is defined for an employee, the tags assigned to the job
position selected are copied to the employee.

Note: If the job position is changed on the same contract, the tags from
old job position will be removed from employee.

Credits
=======

Contributors
------------

* Michael Telahun Makonnen <mmakonnen@gmail.com>
* Savoir-faire Linux
* Fekete Mihai <feketemihai@gmail.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
