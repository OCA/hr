# -*- coding: utf-8 -*-
# © 2014 Eficent
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    move_date = fields.Date(
        string='Force move date',
    )

    @api.onchange('move_date')
    def onchange_move_date(self):
        period_obj = self.env['account.period']
        if self.move_date:
            period_ids = period_obj.find(dt=self.move_date)
            if period_ids:
                self.period_id = period_ids[0]

    @api.multi
    def write(self, vals):
        res = super(HrPayslip, self).write(vals)
        if 'move_id' in vals and vals['move_id']:
            for slip in self:
                if slip.move_date:
                    self.move_id.write({'date': slip.move_date})
                    for move_line in slip.move_id.line_id:
                        move_line.write({'date': slip.move_date})
                else:
                    self.write({'move_date': slip.move_id.date})
        return res


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    move_date = fields.Date(
        string='Force move date',
    )
