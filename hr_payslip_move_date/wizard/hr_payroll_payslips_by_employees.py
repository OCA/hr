# -*- coding: utf-8 -*-
# © 2014 Eficent
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class HrPayslipEmployees(models.TransientModel):

    _inherit = 'hr.payslip.employees'

    @api.multi
    def compute_sheet(self):

        res = super(HrPayslipEmployees, self).compute_sheet()
        payslip_run = self.env['hr.payslip.run'].browse(
            self.env.context['active_id'])
        move_date = payslip_run.move_date
        if move_date:
            period_obj = self.env['account.period']
            period_ids = period_obj.find(dt=move_date)
            if period_ids:
                period_id = period_ids[0]
            else:
                period_id = False
            payslip_run.slip_ids.write({
                'move_date': move_date,
                'period_id': period_id.id,
            })
        return res
