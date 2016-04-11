# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Salton Massally <salton.massally@gmail.com>.
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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


from openerp import fields, models, api
from openerp.exceptions import Warning as UserError


class HrEmployeeTermination(models.Model):
    _name = 'hr.employee.termination'
    _description = 'Data Related to Deactivation of Employee'
    _order = "id DESC"

    _inherit = ['mail.thread', 'ir.needaction_mixin']

    name = fields.Date(
        'Effective Date',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    reason_id = fields.Many2one(
        'hr.employee.termination.reason',
        'Reason',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    notes = fields.Text(
        'Notes',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]}
    )
    employee_id = fields.Many2one(
        'hr.employee',
        'Employee',
        required=True,
        readonly=True
    )
    department_id = fields.Many2one(
        'hr.department',
        "Department",
        store=True,
        readonly=True,
        related='employee_id.department_id'
    )
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('confirm', 'Confirmed'),
            ('cancel', 'Cancelled'),
            ('done', 'Done'),
        ],
        readonly=True,
        default='draft'
    )

    @api.model
    def _needaction_domain_get(self):
        users_obj = self.env['res.users']
        domain = []

        if users_obj.has_group('base.group_hr_user'):
            domain = [('state', 'in', ['draft'])]

        if users_obj.has_group('base.group_hr_manager'):
            if len(domain) > 0:
                domain = ['|'] + domain + [('state', '=', 'confirm')]
            else:
                domain = [('state', '=', 'confirm')]

        return domain

    @api.multi
    def unlink(self):
        res = self.filtered(lambda r: r.state != 'draft')
        if res:
            raise UserError('Employment termination already in progress. '
                            'Use the "Cancel" button instead.')

        return super(HrEmployeeTermination, self).unlink()

    @api.multi
    def state_cancel(self):
        return self.write({'state': 'cancel'})

    @api.multi
    def state_confirm(self):
        return self.write({'state': 'confirm'})

    @api.multi
    def state_done(self):
        today = fields.Date.today()
        for termination in self:
            if today < termination.name:
                raise UserError('Unable to deactivate employee, effective '
                                'date is still in the future!')
            termination.employee_id.end_employment(termination.name)

        return self.write({'state': 'done'})

    @api.model
    def try_terminating_ended(self):
        self.search(
            [('state', '=', 'confirm'),
             ('name', '<=', fields.Date.today())]
        ).state_done()
