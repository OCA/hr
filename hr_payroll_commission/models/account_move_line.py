# -*- coding: utf-8 -*-
#
#  File: models/account_move_line.py
#  Module: hr_payroll_commission
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2015-TODAY Open-Net Ltd.
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from openerp import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    slip_id = fields.Many2one('hr.payslip', string='Pay slip')

    @api.model
    def create(self, vals):
        new_rec = super(AccountMoveLine, self).create(vals)

        # This is for the cases when the first account_move_line
        # doesn't have a partner_id but the others have one.
        if new_rec.account_id.internal_type == 'payable' and \
           new_rec.partner_id:
            query = """update account_move
                       set partner_id=%d
                       where id=%d""" % (
                            new_rec.partner_id.id,
                            new_rec.move_id.id
                        )
            self._cr.execute(query)

        return new_rec

    @api.multi
    def write(self, vals):
        ret = super(AccountMoveLine, self).write(vals)

        # This is for the cases when the first account_move_line
        # doesn't have a partner_id but the others have one.
        for rec in self:
            if rec.account_id.internal_type != 'payable' or not rec.partner_id:
                continue
            account_move_obj = self.env['account.move']
            move_ids = account_move_obj.search([('id', '=', rec.move_id.id)])
            move_ids.write({'partner_id': rec.partner_id.id})
        return ret
