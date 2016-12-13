User data from employee
=======================

When using HR, there are a couple of partners involved per employee: The employee's work address, the employee's private address and the partner assigned to the employee's user (if any). The latter is used to store some data about the user, like the email address. In many cases, it would be more convenient to edit this data from the employee record. This module assumes you assign a (different) partner for the work address to every employee, and synchronizes its values with the employee record. Then you should use this partner record also for the user record. When assigning an existing user, the module will replace this user's partner with the current work address's partner.

Installation
============

As it would be problematic to have work addresses pointing to the company's partner with this module, all employees are updated with either a new partner as work address in case they are not linked to a user, or with the user's partner otherwise. This may take some time if you have a lot of employees. For existing work addresses, the partner's data win, so if your employee has a different email/phone number/image than the corresponding partner, those fields will be overwritten - but only if it is set in the partner.

Also multiple employees pointing to the same partner is problematic. This is fixed by creating new partners for all employees involved, and flagging all of them with the label 'Duplicate work address' and the newly created ones with 'Duplicate work address / Newly created'. Then after installation, search for partners with this labels to do whatever cleanup you consider necessary. After this, it's safe to delete the labels again.

Usage
=====

After installation, updating an employee's `work_email`, `work_phone`, `mobile_phone` and `image` fields transparently changes the linked partner's appropriate field and vice versa. For obvious reasons, the default for the work address being the company's address has been lifted. Partners created through the work address field will have the `employee`-flag set, and the `partner_id` field on the user record filters for this flag.

When creating a user, you can select the existing partner record for your employee, so it will be updated transparently too. Creating a user via the user field in the employee form preselects this partner record.

Credits
=======

Contributors
------------

* Holger Brunn <hbrunn@therp.nl>

Acknowledgements
----------------

* Icon courtesy of http://www.picol.org (refresh.svg) and https://github.com/odoo/odoo/blob/8.0/addons/hr/static/description/icon.png

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
    :alt: Odoo Community Association
    :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
