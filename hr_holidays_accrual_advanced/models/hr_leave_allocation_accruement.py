# Copyright 2018-2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class HrLeaveAllocationAccruement(models.Model):
    """Describes an alteration to the accrual leave balance in order to provide
    definitive explanation how the actual balance was changing over the time.
    """

    _name = 'hr.leave.allocation.accruement'
    _description = 'Leaves Allocation Accruement'

    leave_allocation_id = fields.Many2one(
        string='Leave Allocation',
        comodel_name='hr.leave.allocation',
    )
    days_accrued = fields.Float(
        string='Number of Days',
        readonly=True,
        required=True,
    )
    accrued_on = fields.Date(
        string='Accruement Date',
        readonly=True,
        required=True,
    )
    reason = fields.Char(
        string='Reason',
        readonly=True,
        required=True,
    )
