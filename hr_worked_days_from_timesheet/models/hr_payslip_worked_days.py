# -*- coding: utf-8 -*-
# © 2012 Odoo Canada
# © 2015 Acysos S.L.
# © 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class HrPayslipWorkedDays(models.Model):
    _inherit = 'hr.payslip.worked_days'

    imported_from_timesheet = fields.Boolean(
        string='Imported From Timesheet',
        default=False
    )
    timesheet_sheet_id = fields.Many2one(
        string='Timesheet',
        comodel_name='hr_timesheet_sheet.sheet'
    )
