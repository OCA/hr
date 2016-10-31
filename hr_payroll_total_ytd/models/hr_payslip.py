# -*- coding: utf-8 -*-
# © 2016 Ergobit Consulting (https://www.ergobit.org)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from datetime import datetime
from odoo import fields, models, api, _

to_string = fields.Date.to_string


class HrPayslip(models.Model):

    _inherit = 'hr.payslip'

    @api.multi
    def compute_sheet(self):
        res = super(HrPayslip, self).compute_sheet()
        self.compute_ytd_amounts()
        return res

    @api.multi
    def compute_ytd_amounts(self):
        if not self.line_ids:
            return
        for payslip in self:
            date_from = fields.Date.to_string(datetime(fields.Date.from_string(payslip.date_to).year, 1, 1))
            query = (
                """SELECT pl_1.id, sum(
                    case when p.credit_note then -pl_2.total else pl_2.total end)
                FROM hr_payslip_line pl_1, hr_payslip_line pl_2, hr_payslip p
                WHERE pl_1.id IN %(payslip_line_ids)s
                AND pl_1.salary_rule_id = pl_2.salary_rule_id
                AND pl_2.slip_id = p.id
                AND p.employee_id = %(employee_id)s
                AND p.company_id = %(company_id)s
                AND (p.state = 'done' OR p.id = %(payslip_id)s)
                AND p.date_from >= %(date_from)s
                AND p.date_to <= %(date_to)s
                GROUP BY pl_1.id
                """
            )            
            cr = self.env.cr
            cr.execute(query, {
                'date_from': date_from,
                'date_to': payslip.date_to,
                'payslip_line_ids': tuple(payslip.line_ids.ids),
                'employee_id': payslip.employee_id.id,
                'company_id': payslip.company_id.id,
                'payslip_id': payslip.id,
            })
            res = cr.fetchall()

            line_model = self.env['hr.payslip.line']
            for (line_id, amount_ytd) in res:
                line = line_model.browse(line_id)
                line.amount_ytd = amount_ytd

    @api.multi
    def ytd_amount(self, code):
        """
        Get the total amount since the beginning of the year
        of a given salary rule code.

        :param code: salary rule code
        :return: float
        """
        self.ensure_one()

        date_from = to_string(datetime(fields.Date.from_string(self.date_to).year, 1, 1))
        query = (
            """SELECT sum(
                case when p.credit_note then -pl.total else pl.total end)
            FROM hr_payslip_line pl, hr_payslip p
            WHERE pl.slip_id = p.id
            AND pl.code = %(code)s
            AND p.employee_id = %(employee_id)s
            AND p.company_id = %(company_id)s
            AND p.state = 'done'
            AND p.date_from >= %(date_from)s
            AND p.date_to <= %(date_to)s
            """
        )
        cr = self.env.cr
        cr.execute(query, {
            'date_from': date_from,
            'date_to': self.date_to,
            'company_id': self.company_id.id,
            'employee_id': self.employee_id.id,
            'code': code,
        })

        return cr.fetchone()[0] or 0
