# -*- coding: utf-8 -*-
# © 2014 Savoir-faire Linux (https://www.savoirfairelinux.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api, _
import openerp.addons.decimal_precision as dp


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'


    @api.multi
    def compute_sheet(self):
        super(HrPayslip, self).compute_sheet()
        self.compute_lines_ytd()


    @api.one
    def get_ytd_value(self, code):    # called from payslip
        date_from = self.date_from[0:4] + "-01-01"
        date_to   = self.date_to
#        date_to = fields.Date.today()
        self.env.cr.execute("""SELECT sum(case when hp.credit_note = False then (pl.total) else (-pl.total) end)
                    FROM hr_payslip as hp, hr_payslip_line as pl
                    WHERE hp.employee_id = %s AND hp.state = 'done'
                    AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pl.slip_id AND pl.code = %s""",
                    (self.employee_id, date_from, date_to, code))
        res = self.env.cr.fetchone()
        return res and res[0] or 0.0
                
        
    @api.multi
    def get_line_ytd(self, code):    # called from payslip
        for payslip in self:
            res = 0.0
            date_from = payslip.date_from[0:4] + "-01-01"            
            employee_payslips = self.search([
                    ('employee_id', '=', payslip.employee_id.id),
                    ('date_from', '>=', date_from),
                    ('date_to', '<=', payslip.date_to),
                    ('state', '=', 'done')])
            for emp_payslip in employee_payslips:
                is_refund = emp_payslip.credit_note and -1 or 1
                for line in emp_payslip.line_ids:
                    if line.salary_rule_id.code == code:
                        res += line.total * is_refund
        return res

    @api.multi
    def compute_lines_ytd(self):
        for payslip in self:
            # Create a dict of the required lines that will be used
            # to sum amounts over the payslips
            line_dict = {
                line.salary_rule_id.code: 0 for line in payslip.line_ids}

            # Get the payslips of the employee for the current year
            date_from = payslip.date_from[0:4] + "-01-01"
            
            employee_payslips = self.search([
                    ('employee_id', '=', payslip.employee_id.id),
                    ('date_from', '>=', date_from),
                    ('date_to', '<=', payslip.date_to),
                    ('state', '=', 'done')])

            # Iterate one time over each line of each payslip of the
            # employee since the beginning of the year and sum required
            # lines
            for emp_payslip in employee_payslips:
                is_refund = emp_payslip.credit_note and -1 or 1
                for line in emp_payslip.line_ids:
                    if line.salary_rule_id.code in line_dict:
                        line_dict[line.salary_rule_id.code] += line.total * is_refund

            # For each line in the payslip, write the related total ytd
            for line in payslip.line_ids:
                amount = line_dict[line.salary_rule_id.code] + line.total
                self.env['hr.payslip.line'].browse([line.id])[0].write({'total_ytd': amount})

                
class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    total_ytd = fields.Float('Total Year-to-date', digits_compute=dp.get_precision('Payroll'))
                