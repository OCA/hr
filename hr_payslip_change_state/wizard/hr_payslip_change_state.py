# -*- coding: utf-8 -*-
# © 2016 - Eficent http://www.eficent.com/
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import models, fields, api
from openerp.tools.translate import _
from openerp.exceptions import Warning as UserError


class HrPayslipChangeState(models.TransientModel):

    _name = "hr.payslip.change.state"
    _description = "Change state of a payslip"

    state = fields.Selection(
        selection=[
            ('draft', 'Set to Draft'),
            ('verify', 'Compute Sheet'),
            ('done', 'Confirm'),
            ('cancel', 'Cancel Payslip'),
            ],
        string='Action',
        help='* When the payslip is created the status is \'Draft\'.\
             \n* If the payslip is under verification, the status is '
             '\'Compute Sheet\'. \
             \n* If the payslip is confirmed then status is set to \'Done\'.\
             \n* When user cancel payslip the status is \'Rejected\'.')

    @api.multi
    def change_state_confirm(self):
        record_ids = self.env.context.get('active_ids', False)
        payslip_obj = self.env['hr.payslip']
        new_state = self.state
        records = payslip_obj.browse(record_ids)

        for rec in records:
            if new_state == 'draft':
                if rec.state == 'cancel':
                    rec.signal_workflow("draft")
                else:
                    raise UserError(_("Only rejected payslips can be reset to "
                                      "draft, the payslip %s is in "
                                      "%s state" % (rec.name, rec.state)))
            elif new_state == 'verify':
                if rec.state == 'draft':
                    rec.compute_sheet()
                else:
                    raise UserError(_("Only draft payslips can be verified,"
                                      "the payslip %s is in "
                                      "%s state" % (rec.name, rec.state)))
            elif new_state == 'done':
                if rec.state in ('verify', 'draft'):
                    rec.signal_workflow("hr_verify_sheet")
                else:
                    raise UserError(
                        _("Only payslips in states verify or draft"
                          " can be confirmed, the payslip %s is in "
                          "%s state" % (rec.name, rec.state)))
            elif new_state == 'cancel':
                if rec.state != 'cancel':
                    rec.signal_workflow("cancel_sheet")
                else:
                    raise UserError(_("The payslip %s is already canceled "
                                    "please deselect it" % rec.name))

        return {
            'domain': "[('id','in', ["+','.join(map(str, record_ids))+"])]",
            'name': _('Payslips'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.payslip',
            'view_id': False,
            'context': False,
            'type': 'ir.actions.act_window'
        }
