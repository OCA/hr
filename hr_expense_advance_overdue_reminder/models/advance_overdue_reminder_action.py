# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AdvanceOverdueReminderAction(models.Model):
    _name = 'advance.overdue.reminder.action'
    _inherit = 'overdue.reminder.action'

    reminder_count = fields.Integer(
        compute='_compute_expense_count', store=True,
        string='Number of Advance')
    reminder_ids = fields.One2many(
        comodel_name='hr.expense.sheet.overdue.reminder',
        inverse_name='action_id',
        readonly=True)

    @api.depends('reminder_ids')
    def _compute_expense_count(self):
        ao_object = self.env['hr.expense.sheet.overdue.reminder']
        rg_res = ao_object.read_group(
            [('action_id', 'in', self.ids), ('expense_sheet_id', '!=', False)],
            ['action_id'], ['action_id'])
        mapped_data = dict([
            (x['action_id'][0], x['action_id_count']) for x in rg_res])
        for rec in self:
            rec.reminder_count = mapped_data.get(rec.id, 0)
