Leave Accruals
==============

This module adds leave accruals on employees and a mechanism to compute these
automaticaly.

The amounts for a leave type can be accruded
in cash, in hours or both.


Installation
============

Nothing to do except install the module


Configuration
=============

 - Go to: Human Ressources -> Configuration -> Leaves Types
 - Select a leave type over which you wish to accrued amounts.
 - In the form view, go to the "Leave Accruals" tab.
 - Select payslip lines over which the leave type will be accruded.
 - If a salary rule gives a positive amount and you need to decrease the leave accrual from this amount,
   you need to set the field "Substract Amount" True.

The leave allocation system may be used to increase the hours accruded for a leave type.
For this, the field "Increase Accruals on Allocations" on the leave type must be True.
An example of use for this feature is for sick leaves.


Usage
=====

Compute your payslips and the amounts are automatically accruded in the related employee leave accrual.
In the employee form, there is a tab "Leave Accruals", which shows amounts accruded per leave type.


Known issues / Roadmap
======================

None


Credits
=======

Contributors
------------

.. image:: http://sflx.ca/logo
   :alt: Savoir-faire Linux
   :target: http://sflx.ca

* David Dufresne <david.dufresne@savoirfairelinux.com>
* Maxime Chambreuil <maxime.chambreuil@savoirfairelinux.com>
* Pierre Lamarche <pierre.lamarche@savoirfairelinux.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.