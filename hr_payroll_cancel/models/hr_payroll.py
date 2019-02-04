# Copyright 2014 - Vauxoo http://www.vauxoo.com/
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
#   (<http://www.serpentcs.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval as eval


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    refunded_id = fields.Many2one(
        'hr.payslip',
        string='Refunded Payslip',
        readonly=True
    )

    @api.multi
    def refund_sheet(self):
        res = super(HrPayslip, self).refund_sheet()
        self.write({'refunded_id': eval(res['domain'])[0][2][0] or False})
        return res

    @api.multi
    def action_payslip_cancel(self):
        for payslip in self:
            if payslip.refunded_id and payslip.refunded_id.state != 'cancel':
                raise ValidationError(_("""To cancel the Original Payslip the
                    Refunded Payslip needs to be canceled first!"""))
            if payslip.move_id.journal_id.update_posted:
                payslip.move_id.button_cancel()
                payslip.move_id.unlink()
            else:
                payslip.move_id.reverse_moves()
                payslip.move_id = False
        return self.write({'state': 'cancel'})
