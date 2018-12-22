This module allows the user to cancel a payslip whatever the previous state is
without doing a refund. When the user cancel the journal entry is deleted
and  the payslip state is set to rejected. Then the user is able to set the
state to draft again and later on he/she is able to confirm again the payslip.

If there’s a refund for a payslip the user should not cancel the entry because
the refund would still be confirm. In that case, the user have either to
confirm again the payslip or cancel the refund.

