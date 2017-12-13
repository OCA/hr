.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

==========================================
hr_employee_data_from_work_address_nl_name
==========================================

This module extends the module hr_employee_data_from_work_address with the
fields provided by the module l10n_nl_hr_employee_name.
The module hr_employee_data_from_work address , takes the info from  the
employee work address (partner) and syncs it with the employee data. It also
takes the employee's work address and replaces it with the  partner of the user
associated to the employee.
l10n_nl_hr_employee_name adds to employee several fields (infix, initial, split
first and last name) in order to obtain dutch naming style.

This module extends the sync of the employee work partner and the employee
data with these new fields.


Installation
============

To install this module, you need to:

#. do this ...

Configuration
=============

To configure this module, you need to:

#. go to ...

Usage
=====

To use this module, you need to:

#. go to ...
.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
    :alt: Try me on Runbot
    :target: https://runbot.odoo-community.org/runbot/{repo_id}/8.0

.. repo_id is available in https://github.com/OCA/maintainer-tools/blob/master/tools/repos_with_ids.txt

Known issues / Roadmap
======================

* ...

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

* Giovanni Francesco Capalbo <giovanni@therp.nl>  

Do not contact contributors directly about help with questions or problems concerning this addon, but use the `community mailing list <mailto:community@mail.odoo.com>`_ or the `appropriate specialized mailinglist <https://odoo-community.org/groups>`_ for help, and the bug tracker linked in `Bug Tracker`_ above for technical issues.

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
