# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models, fields


class HrPayslipWorkedDays(models.Model):
    _inherit = 'hr.payslip.worked_days'

    import_from_attendance = fields.Boolean(
        string='Imported From Timesheet',
        default=False,
    )
