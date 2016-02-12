.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Payroll Commissions and Reinbursements

======================================

This module allows you to add commission and reimbursement to payslip

** Features list :**
    * Add Worked Hours to contract.
    * Add Hourly Rate to contract.
    * Compute the Wage of contract, based on Worked Hours and Hourly Rate.
    * Add commision rate, commision and reimbursement to contract.
    * Link Expenses and Invoices to Payslip.

** For further information:**
    * Commissions and reimbursements management: http://open-net.ch/blog/la-comptabilite-salariale-suisse-avec-odoo-1/post/salaires-avec-odoo-commissions-et-notes-de-frais-78

** Remarks: **
    * As this module proposes its own report (same as the original, but with its own footer), don't forget to make it non-updatable.

** Usage: **

Commision
    * To add commission to the payslip, you need to add a rate into the employee's contract. You also need to add a the rule COMM to the contract.
    * When you have this properly setup, you just have to compute your payslip to find COMM into the list.
Reimbursement
    * To add reimbursement to the employee's payslip, you need to add the REIMB rule to the corresponding contract.
    * Then you just need to compute your payslip to find REIMB into the list.



Known issues / Roadmap
----------------------

V1.0.0: 2014-11-07/dco
    * Module functions splitted from l10n_ch_hr_payroll.

Contributors
------------

* Sebastien Gendre <sge@open-net.ch>
* Yvon-Philippe Crittin <cyp@open-net.ch>
* David Coninckx <dco@open-net.ch>

Bug Tracker
-----------

Bugs are tracked on `GitHub Issues <https://github.com/OCA/hr-timesheet/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/hr-timesheet/issues/new?body=module:%20crm_timesheet%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

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
