.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Applicants implicit Partner
===========================

Automatically create a Partner for Applicants.

When an Applicant is created, a related Partner for it is automatically
created.

Duplicate personal data is directly stored in the related Partner record,
but is still available in the Applicant model.

As an additional advantage, it is easier now to add other personal and
address details to the Applicant form, such as the photo image or the
address details.


Configuration
=============

You may like to customize your Applicants form view to add to it some
Partner fields relevant for your use case.


Usage
=====

Some fields in the Applicant form are now mapped to the corresponding fields
in the partner form. For example, editing the Phone or Email in one place will
implicitly change it in the other.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/116/8.0


Known issues / Roadmap
======================

* Creating an Employee from the Applicant should reuse the Partner data. Maybe
  do this working with ``hr_employee_data_from_work_address``.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/hr/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/hr/issues/new?body=module:%20hr_recruitment_partner%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Daniel Reis


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
