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

from openerp.osv import fields, orm
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime
strftime = datetime.strftime


class hr_contract_job(orm.Model):
    _inherit = 'hr.contract.job'

    def _get_current_hourly_rate(
        self, cr, uid, ids, field_name, arg, context=None
    ):
        now = strftime(datetime.now().date(), DEFAULT_SERVER_DATE_FORMAT)
        res = {}
        for i in ids:
            contract_job = self.browse(cr, uid, i, context=context)
            contract = contract_job.contract_id
            if contract_job.hourly_rate_class_id and \
                    contract.salary_computation_method == 'hourly_rate':
                rate_class = contract_job.hourly_rate_class_id
                rates = [
                    r for r in rate_class.line_ids
                    if(
                        r.date_start <= now
                        and (
                            not r.date_end
                            or now <= r.date_end
                        )
                    )
                ]
                res[i] = rates and rates[0].rate or 0
            else:
                res[i] = False
        return res

    _columns = {
        'hourly_rate_class_id': fields.many2one(
            'hr.hourly.rate.class',
            'Hourly Rate Class'
        ),
        'hourly_rate': fields.function(
            _get_current_hourly_rate,
            type='float',
            method=True,
            string='Hourly Rate',
        ),
    }
