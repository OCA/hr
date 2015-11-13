# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2015 Salton Massally (<smassally@idtlabs.sl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from openerp import models, fields, api


class PrintRunContribRegister(models.TransientModel):
    _name = 'print.run.contrib_register'
    _description = 'Print Contribution Register'

    contrib_register_ids = fields.Many2many(
        'hr.contribution.register',
        string="Contribution Registers"
    )

    @api.multi
    def print_contrib_register(self):
        self.ensure_one()
        run_id = self.env.context['active_id']
        run = self.env['hr.payslip.run'].browse(run_id)

        datas = {
            'model': 'hr.contribution.register',
            'ids': self.contrib_register_ids.ids,
            'form': {
                'date_from': run.date_start,
                'date_to': run.date_end,
                'slip_ids': run.slip_ids.ids,
            }
        }
        report_obj = self.env['report'].with_context(
            active_ids=self.contrib_register_ids.ids,
            active_model='hr.contribution.register')
        return report_obj.get_action(
            self.contrib_register_ids,
            'hr_payroll_report_contrib_register.report_contributionregister',
            data=datas
        )
