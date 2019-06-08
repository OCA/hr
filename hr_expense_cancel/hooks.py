# Copyright 2019 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    """ Trying to fill the source expense sheet in payments """
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})

        for sheet in env['hr.expense.sheet'].search([]):
            expense_lines = sheet.expense_line_ids
            if any(exp.payment_mode == 'own_account' for exp in expense_lines):
                amls = sheet.account_move_id.mapped('line_ids')
                reconciles = amls.mapped('full_reconcile_id')
                for reconcile in reconciles:
                    aml_payment = reconcile.reconciled_line_ids.filtered(
                        lambda r: r not in amls)
                    payment = aml_payment.mapped('payment_id')
                    payment.write({'expense_sheet_id': sheet.id})
