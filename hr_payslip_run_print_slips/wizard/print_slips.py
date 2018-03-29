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
from openerp import models, api


class PrintRunSlips(models.TransientModel):
    _name = 'print.run.slips'
    _description = 'Print Pay Slips'

    @api.multi
    def print_slips(self):
        self.ensure_one()
        run_id = self.env.context['active_id']
        run = self.env['hr.payslip.run'].browse(run_id)

        datas = {
            'model': 'hr.payslip',
            'ids': run.slip_ids.ids,
        }
        report_obj = self.env['report'].with_context(
            active_ids=run.slip_ids.ids,
            active_model='hr.payslip'
        )
        if self.env.context.get('print_details'):
            return report_obj.get_action(
                run.slip_ids,
                'hr_payroll.report_payslipdetails',
                data=datas
            )
        else:
            return report_obj.get_action(
                run.slip_ids,
                'hr_payroll.report_payslip',
                data=datas
            )
