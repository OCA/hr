This module extends the functionality of hr_work_entry_contract in order to display corresponding timesheet duration on work entries.

Also a check is made for discrepancy and the work entries are displayed hatched on calendar view in case :
1. no timesheet has been recorded on some day (assuming that leaves also create timesheets with native Odoo module project_timesheet_holidays)
1. more hours have been recorded than duration of the work entry
