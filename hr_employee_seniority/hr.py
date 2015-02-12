# -*- coding:utf-8 -*-
#
#
#    Copyright (C) 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
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
#

from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

from openerp.osv import fields, orm
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DATEFORMAT
from openerp.tools.translate import _


class hr_employee(orm.Model):

    _inherit = 'hr.employee'

    def _get_contracts_list(self, employee):
        """Return list of contracts in chronological order"""

        contracts = []
        for c in employee.contract_ids:
            l = len(contracts)
            if l == 0:
                contracts.append(c)
            else:
                dCStart = datetime.strptime(c.date_start, OE_DATEFORMAT).date()
                i = l - 1
                while i >= 0:
                    dContractStart = datetime.strptime(
                        contracts[i].date_start, OE_DATEFORMAT).date()
                    if dContractStart < dCStart:
                        contracts = contracts[:i + 1] + [c] + contracts[i + 1:]
                        break
                    elif i == 0:
                        contracts = [c] + contracts
                    i -= 1

        return contracts

    def _get_days_in_month(self, d):

        last_date = d - timedelta(days=(d.day - 1)) + relativedelta(
            months=1) + relativedelta(days=-1)
        return last_date.day

    def get_months_service_to_date(
            self, cr, uid, ids, dToday=None, context=None):
        """Returns a dictionary of floats. The key is the employee id,
        and the value is number of months of employment.
        """

        res = dict.fromkeys(ids, 0)
        if dToday is None:
            dToday = date.today()
        employee_pool = self.pool['hr.employee']
        for ee in employee_pool.browse(cr, uid, ids, context=context):

            delta = relativedelta(dToday, dToday)
            contracts = self._get_contracts_list(ee)
            if len(contracts) == 0:
                res[ee.id] = (0.0, False)
                continue

            dInitial = datetime.strptime(
                contracts[0].date_start, OE_DATEFORMAT).date()

            if ee.initial_employment_date:
                dFirstContract = dInitial
                dInitial = datetime.strptime(
                    ee.initial_employment_date, OE_DATEFORMAT).date()
                if dFirstContract < dInitial:
                    raise orm.except_orm(
                        _('Employment Date mismatch!'),
                        _("The initial employment date cannot be after the "
                          "first contract in the system.\n"
                          "Employee: %s", ee.name))

                delta = relativedelta(dFirstContract, dInitial)

            for c in contracts:
                dStart = datetime.strptime(c.date_start, '%Y-%m-%d').date()
                if dStart >= dToday:
                    continue

                # If the contract doesn't have an end date, use today's date
                # If the contract has finished consider the entire duration of
                # the contract, otherwise consider only the months in the
                # contract until today.
                #
                if c.date_end:
                    dEnd = datetime.strptime(c.date_end, '%Y-%m-%d').date()
                else:
                    dEnd = dToday
                if dEnd > dToday:
                    dEnd = dToday

                delta += relativedelta(dEnd, dStart)

            # Set the number of months the employee has worked
            date_part = float(delta.days) / float(
                self._get_days_in_month(dInitial))
            res[ee.id] = (
                float((delta.years * 12) + delta.months) + date_part, dInitial)

        return res

    def _get_employed_months(
            self, cr, uid, ids, field_name, arg, context=None):

        res = dict.fromkeys(ids, 0.0)
        _res = self.get_months_service_to_date(cr, uid, ids, context=context)
        for k, v in _res.iteritems():
            res[k] = v[0]
        return res

    def _search_amount(self, cr, uid, obj, name, args, context):
        ids = set()
        for cond in args:
            amount = cond[2]
            if isinstance(cond[2], (list, tuple)):
                if cond[1] in ['in', 'not in']:
                    amount = tuple(cond[2])
                else:
                    continue
            else:
                if cond[1] in [
                        '=like',
                        'like',
                        'not like',
                        'ilike',
                        'not ilike',
                        'in',
                        'not in',
                        'child_of', ]:
                    continue

            cr.execute("select id from hr_employee having %s %%s" %
                       (cond[1]), (amount,))
            res_ids = set(id[0] for id in cr.fetchall())
            ids = ids and (ids & res_ids) or res_ids
        if ids:
            return [('id', 'in', tuple(ids))]
        return [('id', '=', '0')]

    _columns = {
        'initial_employment_date': fields.date(
            'Initial Date of Employment',
            groups=False,
            help='Date of first employment if it was before the start of the '
                 'first contract in the system.',
        ),
        'length_of_service': fields.function(
            _get_employed_months,
            type='float',
            method=True,
            groups=False,
            string='Length of Service',
        ),
    }
