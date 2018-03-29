.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

========================
Employee Loan Management
========================

This module add functionality to:

1. Manage employee loan request
2. Calculate loan repayment schedule
3. Track employee loan disburstment
4. Track employee loan repayment

**Loan Disburstment**

Disbursement is the act of paying out or disbursing money, such as money paid out to run a business, 
cash expenditures, dividend payments, and/or the amounts that a lawyer might have to pay out 
on a person's behalf in connection with a transaction.

http://www.investopedia.com/terms/d/disbursement.asp

**Loan Principle Amount**

The amount of debt, exclusive of interest, remaining on a loan.

http://www.ucop.edu/loan-programs/resources/loan-terminology-glossary.html

**Loan Repayment Schedule**

Detailed outline of a borrower's loan agreement with a lender that shows the original loan amount, 
when payments are due, and how much of the payment goes to the principal and interest repayment. 
This statement may be provided on a monthly basis or may be issued when the loan is originally acquired.

http://www.investorwords.com/8680/repayment_schedule.html

**Loan Repayment**

Repayment is the act of paying back money previously borrowed from a lender

http://www.investopedia.com/terms/r/repayment.asp

Installation
============

To install this module, you need to:

1.  Clone the branch 8.0 of the repository https://github.com/OCA/hr
2.  Add the path to this repository in your configuration (addons-path)
3.  Update the module list
4.  Go to menu *Setting -> Modules -> Local Modules*
5.  Search For *Employee Loan Management*
6.  Install the module

Configuration
=============

**Employee Loan Type**

To configure employee loan type, you need to:

1. Go to menu *Human Resource -> Configuration -> Employee Loan -> Employee Loan Type*
2. Create new employee loan type


Usage
=====

Create Employee Loan Request
----------------------------

1. Go to menu *Human Resources -> Employee Loan -> My Loan*
2. Create employee loan
3. Click *Confirm* button to confirm employee loan request

Approve Employee Loan Request
-----------------------------

1. Go to menu *Human Resources -> Employee Loan -> My Loan*
2. Open employee loan data with *Waiting for Approval* status
3. Click *Approve* button

Odoo will create journal entry with bellow configuration:

Loan Principle Receivable Dr.
    Loan Realization Cr.

Note:
*Loan principle receivable* will be generated as much as number of payment schedule

Employee Loan Disburstment
--------------------------

Employee loan can be realized by reconcile *Loan Realization Move Line*
created from step above. You can reconcile them by using any accounting
method provided by Odoo, such as: (1) bank statement, (2) voucher, or
(3) manualy creating journal entry and reconciliation.


Employee Loan Principle Repayment
---------------------------------

Employee loan's principle can be paid by reconcile *Principle Receivable Move Line*
created from approval steap above. You can reconcile them by using any accounting
method provided by Odoo, such as: (1) bank statement, (2) voucher, or
(3) manualy creating journal entry and reconciliation.


Employee Loan Interest Realization
----------------------------------

Through *Employee Loan* menu:

1. Go to menu *Human Resources -> Employee Loan -> Employee Loan*
2. Look through loan repayment schedule table
3. Click *Realize Interest* button for each interest schedule that need to be realized
4. Select *Realization Date* on *Realize Interest* form wizard
5. Click *Realize* button

Through *Repayment Schedule* menu:

1. Go to menu *Human Resources -> Employee Loan -> Repayment Schedule*
2. Activate *Active Loan* filter
3. Open repayment schedule that need to be realized
4. Click *Realize Interest* button


Through *Repayment Schedule* menu, using context action:

1. Go to menu *Human Resources -> Employee Loan -> Repayment Schedule*
2. Activate *Active Loan* filter
3. Select repayment schedule that need to be realized
4. Click *More* button
5. Click *Realize Interest* button

Odoo will create journal entry with bellow configuration:

Loan Interest Receivable Dr.
    Interest Income Cr.

Employee Loan Interest Repayment
--------------------------------

Employee loan's interest can be paid by reconcile *Principle Receivable Move Line*
created from approval steap above. You can reconcile them by using any accounting
method provided by Odoo, such as: (1) bank statement, (2) voucher, or
(3) manualy creating journal entry and reconciliation.

Delete Loan
-----------

You can only delete loan data, if:

1. State equal to *cancel*, and
2. No loan number assigned

Note for administrator:
Unlink policy could be override by using *force_unlink* context


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/116/8.0


Known issues / Roadmap
======================

1. Mechanism for set to draft or manage loan revision will be handled on other module
2. No support for multi-currency
3. No direct integration to payslip. Loan repayment has to be done via accounting reconciliation.

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
