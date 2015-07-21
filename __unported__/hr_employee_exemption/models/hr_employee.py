# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Savoir-faire Linux. All Rights Reserved.
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

from openerp.osv import orm, fields


class HrEmployee(orm.Model):
    _inherit = 'hr.employee'

    _columns = {
        'exemption_ids': fields.one2many(
            'hr.employee.exemption',
            'employee_id',
            'Income Tax Exemptions',
            groups='base.group_hr_manager',
        ),
    }

    def exempted_from(self, cr, uid, ids, exemption, date, context=None):
        """
        The method to call from a salary rule to check whether an employee
        is exempted from a source deduction

        :type exemption: hr.income.tax.exemption browse record
        """

        if isinstance(ids, (int, long)):
            ids = [ids]

        assert len(ids) == 1, 'must be called with a single employee'

        employee = self.browse(cr, uid, ids[0], context=context)

        for e in employee.exemption_ids:
            if (
                e.exemption_id == exemption and
                e.date_from <= date and
                (not e.date_to or date <= e.date_to)
            ):
                return True

        return False
