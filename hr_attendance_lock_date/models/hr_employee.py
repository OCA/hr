# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    attendance_lock_date = fields.Datetime('Attendance lock date')

    @api.model
    def _cron_lock_all_employee(self):
        """ Must be called from ir.cron """
        for employee in self.search([]):
            employee.attendance_lock_date = fields.Datetime.now()
        return True
