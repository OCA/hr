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

from openerp.osv import fields, orm
from openerp.tools.translate import _


class hr_attendance(orm.Model):

    _name = 'hr.attendance'
    _inherit = 'hr.attendance'

    _columns = {
        'state': fields.selection((
            ('draft', 'Unverified'), (
                'verified', 'Verified'), ('locked', 'Locked'),
        ), 'State', required=True, readonly=True),
    }

    _defaults = {
        'state': 'draft',
    }

    def is_locked(self, cr, uid, employee_id, utcdt_str, context=None):

        res = False
        pp_obj = self.pool.get('hr.payroll.period')
        ee_data = self.pool.get('hr.employee').read(
            cr, uid, employee_id,
            ['contract_ids'], context=context)
        pp_ids = pp_obj.search(cr, uid, [
            ('state', 'in', [
                'locked', 'generate', 'payment', 'closed']),
            '&', ('date_start', '<=', utcdt_str),
            ('date_end', '>=', utcdt_str),
        ], context=context)
        for pp in pp_obj.browse(cr, uid, pp_ids, context=context):
            pp_contract_ids = [c.id for c in pp.schedule_id.contract_ids]
            for c_id in ee_data['contract_ids']:
                if c_id in pp_contract_ids:
                    res = True
                    break
            if res is True:
                break

        return res

    def create(self, cr, uid, vals, context=None):

        if self.is_locked(
            cr, uid, vals['employee_id'], vals['name'], context=context
        ):
            ee_data = self.pool.get(
                'hr.employee').read(cr, uid, vals['employee_id'], ['name'],
                                    context=context)
            raise orm.except_orm(
                _('The period is Locked!'),
                _("You may not add an attendance record to a locked period.\n"
                  "Employee: %s\n"
                  "Time: %s") % (ee_data['name'], vals['name']))

        return super(hr_attendance, self).create(
            cr, uid, vals, context=context)

    def unlink(self, cr, uid, ids, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]

        for punch in self.browse(cr, uid, ids, context=context):
            if punch.state in ['verified', 'locked']:
                raise orm.except_orm(
                    _('The Record cannot be deleted!'),
                    _("You may not delete a record that is in a %s state:\n"
                      "Employee: %s, Date: %s, Action: %s")
                    % (
                        punch.state, punch.employee_id.name, punch.name,
                        punch.action))

        return super(hr_attendance, self).unlink(cr, uid, ids, context=context)

    def write(self, cr, uid, ids, vals, context=None):

        if isinstance(ids, (int, long)):
            ids = [ids]

        for punch in self.browse(cr, uid, ids, context=context):
            if (
                punch.state in ['verified', 'locked'] and
                (
                    vals.get('name') or vals.get('action') or
                    vals.get('employee_id'))
            ):
                raise orm.except_orm(
                    _('The record cannot be modified!'),
                    _("You may not write to a record that is in a %s state:\n"
                      "Employee: %s, Date: %s, Action: %s")
                    % (
                        punch.state, punch.employee_id.name, punch.name,
                        punch.action))

        return super(hr_attendance, self).write(
            cr, uid, ids, vals, context=context)
