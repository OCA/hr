======================
 HR Payslip YTD Amount
======================
    
This module adds a field in payslip lines for year-to-date amounts.

    * The purpose of this module is to eliminate redondant rules that calculate the year-to-date value of other rules.  
    * The year-to-date value is calculated only for the rules that appear on payslip
    * The year-to-date value is calculated in 2 steps:
    *       step 1:  before the computation of the payslip, we calculate the ytd value without the current payslip. So we can use this ytd value in other rules during payslip computation.
    *       step 2:  after the computation of the payslip, we add the value of eavch rule to the ytd calculated in step 1.
    

Credits
=======

Contributors
------------
* David Dufresne <david.dufresne@savoirfairelinux.com>
* Pierre Lamarche <pierre.lamarche@savoirfairelinux.com>
* Bassirou Ndaw <b.ndaw@ergobit.org>

Sponsors
--------
* `ERGOBIT Consulting <https://ergobit.org/>`_

Further information
===================

Usage instructions: `<doc/index.rst>`_

Changelog: `<doc/changelog.rst>`_


