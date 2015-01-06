# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Savoir-faire Linux. All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by
#    the Free Software Foundation, either version 3 of the License, or
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

import itertools


class PayrollBrowsableObject(object):
    """
    The same as in hr_payroll module
    """
    def __init__(self, pool, cr, uid, dict):
        self.pool = pool
        self.cr = cr
        self.uid = uid
        self.dict = dict

    def __getattr__(self, attr):
        return attr in self.dict and self.dict.__getitem__(attr) or 0.0


class PayslipsBrowsableObject(PayrollBrowsableObject):
    """
    Similar as in hr_payroll module
    """
    def __init__(self, pool, cr, uid, company_id, dict):
        self.company_id = company_id
        super(PayslipsBrowsableObject, self).__init__(
            pool, cr, uid, dict
        )

    def sum(self, code, from_date, to_date, company_ids):
        """
        Sum over every payslip line that match the given code
        for a given list of companies for a given period.
        """
        cr, uid, context = self.cr, self.uid, self.context

        if isinstance(company_ids, (int, long)):
            company_ids = [company_ids]

        payslip_ids = self.pool['hr.payslip'].search(
            cr, uid, [
                ('company_id', 'in', company_ids),
                ('date_from', '>=', from_date),
                ('date_to', '<=', to_date),
                ('state', '=', 'done'),
            ], context=context)

        payslip_line_ids = self.pool['hr.payslip.line'].search(
            cr, uid, [
                ('slip_id', 'in', payslip_ids),
                ('code', '=', code),
            ], context=context)

        payslip_lines = self.pool['hr.payslip.line'].browse(
            cr, uid, payslip_line_ids, context=context)

        res = 0
        for line in payslip_lines:
            if line.slip_id.credit_note:
                res -= line.total
            else:
                res += line.total

        return res

    def sum_between_range(
            self, code, from_date, to_date,
            min_range, max_range, company_ids,
            count_employees=False):
        """
        Sum amounts in payslips for a period of time.
        For each employee, get the amount included in a range.

        Example: A contribution is based on the wage of each employee
        between 3500 and 52500. The company has 2 employees. One of them
        earns 40k, the other 70k. The method will return
        (52500 - 3500) + (40000 - 3500)

        :param count_employees is True: return only the number of
        employees that have an amount within given range
        """
        cr, uid, context = self.cr, self.uid, self.context

        if isinstance(company_ids, (int, long)):
            company_ids = [company_ids]

        payslip_obj = self.pool['hr.payslip']
        payslip_ids = payslip_obj.search(
            cr, uid, [
                ('company_id', 'in', company_ids),
                ('date_from', '>=', from_date),
                ('date_to', '<=', to_date),
                ('state', '=', 'done'),
            ], context=context)

        # Get payslips grouped by employee
        payslips_per_employee = itertools.groupby(
            payslip_obj.browse(cr, uid, payslip_ids, context=context),
            lambda ps: ps.employee_id.id,
        )

        res = 0
        number_employees = 0
        for emp_id, payslips in payslips_per_employee:
            payslip_line_ids = self.pool['hr.payslip.line'].search(
                cr, uid, [
                    ('slip_id', 'in', [ps.id for ps in payslips]),
                    ('code', '=', code),
                ], context=context)

            payslip_lines = self.pool['hr.payslip.line'].browse(
                cr, uid, payslip_line_ids, context=context)

            sub_total = 0
            for line in payslip_lines:
                if line.slip_id.credit_note:
                    sub_total -= line.total
                else:
                    sub_total += line.total

            sub_total = min(sub_total, max_range)
            sub_total = max(0, sub_total - min_range)
            res += sub_total

            if sub_total > 0:
                number_employees += 1

        if count_employees:
            return number_employees

        return res
