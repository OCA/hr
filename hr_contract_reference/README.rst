.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3  

=====================
HR Contract Reference
=====================

This module was written to extend the functionality of employees contracts
to support sequence of contract reference which will be generated
automatically from the sequence predefined.

Installation
============

To install this module, you need to:

1.  Clone the branch 9.0 of the repository https://github.com/OCA/hr
2.  Add the path to this repository in your configuration (addons-path)
3.  Update the module list
4.  Go to menu *Apps*
5.  Search For *HR Contract Reference*
6.  Install the module

Configuration
=============

If you want to modify the format of the sequence, go to
Settings -> Technical -> Sequences & Identifiers -> Sequences
and search for the "Contract Reference" sequence, where you modify
its prefix and numbering formats.

Usage
=====

When you will create a new employee contract, the field reference will be
assigned automatically with the next number of the predefined sequence.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/116/9.0

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
* Michael Viriyananda <viriyananda.michael@gmail.com>

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
