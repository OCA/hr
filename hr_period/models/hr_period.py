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
from openerp.tools.translate import _

from .hr_fiscal_year import get_schedules


class HrPeriod(orm.Model):
    _name = 'hr.period'
    _description = 'HR Payroll Period'

    _columns = {
        'name': fields.char(
            'Name', required=True,
            readonly=True, states={'draft': [('readonly', False)]},
        ),
        'number': fields.integer(
            'Number', required=True,
            readonly=True, states={'draft': [('readonly', False)]},
        ),
        'date_start': fields.date(
            'Start of Period', required=True,
            readonly=True, states={'draft': [('readonly', False)]},
        ),
        'date_stop': fields.date(
            'End of Period', required=True,
            readonly=True, states={'draft': [('readonly', False)]},
        ),
        'date_payment': fields.date(
            'Date of Payment', required=True,
            readonly=True, states={'draft': [('readonly', False)]},
        ),
        'fiscalyear_id': fields.many2one(
            'hr.fiscalyear', 'Fiscal Year', required=True,
            readonly=True, states={'draft': [('readonly', False)]},
            ondelete='cascade',
        ),
        'state': fields.selection(
            [('draft', 'Draft'), ('open', 'Open'), ('done', 'Closed')],
            'Status', readonly=True, required=True,
        ),
        'company_id': fields.related(
            'fiscalyear_id', 'company_id', type='many2one',
            relation='res.company', string='Company', store=True,
            readonly=True, states={'draft': [('readonly', False)]},
        ),
        'schedule_pay': fields.selection(
            get_schedules, 'Scheduled Pay', required=True,
            readonly=True, states={'draft': [('readonly', False)]},
        ),
        'payslip_ids': fields.one2many(
            'hr.payslip', 'hr_period_id', 'Payslips',
            readonly=True,
        ),
    }

    _defaults = {
        'state': 'draft',
    }

    _order = 'date_start'

    def get_next_period(
        self, cr, uid, company_id, schedule_pay, context=None
    ):
        """ Get the next payroll period to process
        :rtype: hr.period browse record
        """
        ids = self.search(cr, uid, [
            ('company_id', '=', company_id),
            ('schedule_pay', '=', schedule_pay),
            ('state', '=', 'open'),
        ], order='date_start', limit=1, context=context)

        return self.browse(cr, uid, ids[0], context=context) if ids else False

    def button_set_to_draft(self, cr, uid, ids, context=None):
        for period in self.browse(cr, uid, ids, context=context):
            if period.payslip_ids:
                raise orm.except_orm(
                    _('Warning'),
                    _('You can not set to draft a period that already '
                        'has payslips computed'))

        self.write(cr, uid, ids, {'state': 'draft'}, context=context)

    def button_open(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'open'}, context=context)

    def button_close(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'done'}, context=context)

        for period in self.browse(cr, uid, ids, context=context):
            fy = period.fiscalyear_id

            # If all periods are closed, close the fiscal year
            if all(p.state == 'done' for p in fy.period_ids):
                fy.write({'state': 'done'})

    def button_re_open(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'open'}, context=context)

        for period in self.browse(cr, uid, ids, context=context):
            fy = period.fiscalyear_id
            if fy.state != 'open':
                fy.write({'state': 'open'})
