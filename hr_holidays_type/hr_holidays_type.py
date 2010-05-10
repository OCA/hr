# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
import time

from osv import fields, osv
from tools.translate import _

class hr_holidays_status(osv.osv):
    _inherit = "hr.holidays.status"

    def get_days(self, cr, uid, ids, employee_id, return_false, context={}):
        res = {}
        for record in self.browse(cr, uid, ids, context):
            res[record.id] = {}
            max_leaves = leaves_taken = 0
            if not return_false:
                cr.execute("""SELECT type, sum(number_of_days) FROM hr_holidays WHERE employee_id = %s AND state='validate' AND holiday_status_id = %s and type='add' GROUP BY type""", (str(employee_id), str(record.id)))
                for line in cr.fetchall():
                    if line[0] =='add':
                        max_leaves = line[1]
                cr.execute("""SELECT type, sum(h.number_of_days) from hr_holidays as h left join hr_holidays_line as t on t.holiday_id=h.id where employee_id = %s AND state='validate' AND t.holiday_status_id = %s and type='remove' GROUP BY type""",(str(employee_id), str(record.id)))
                for line in cr.fetchall():
                    if line[0] =='remove':
                        leaves_taken = -line[1]
            res[record.id]['max_leaves'] = max_leaves
            res[record.id]['leaves_taken'] = leaves_taken
            res[record.id]['remaining_leaves'] = max_leaves - leaves_taken
        return res

hr_holidays_status()

class hr_holidays_line(osv.osv):
    _name = 'hr.holidays.line'
    _description = 'hr.holidays.line'
    _columns = {
        'holiday_status_id': fields.many2one("hr.holidays.status", "Leave Type",),
        'date_from': fields.datetime('Start Date'),
        'date_to': fields.datetime('End Date'),
        'number_of_days': fields.float('Number of Days'),
        'holiday_id': fields.many2one('hr.holidays', 'Holiday'),
                }

    def onchange_sec_id(self, cr, uid, ids, status, context={}):
        warning = {}
        if status:
            brows_obj = self.pool.get('hr.holidays.status').browse(cr, uid, [status])[0]
            if brows_obj.categ_id and brows_obj.categ_id.section_id and not brows_obj.categ_id.section_id.allow_unlink:
                warning = {
                    'title': "Warning for ",
                    'message': "You won\'t be able to cancel this leave request because the CRM Section of the leave type disallows."
                        }
        return {'warning': warning}

    def onchange_date_from(self, cr, uid, ids, date_to, date_from):
        result = {}
        if date_to and date_from:
            from_dt = time.mktime(time.strptime(date_from,'%Y-%m-%d %H:%M:%S'))
            to_dt = time.mktime(time.strptime(date_to,'%Y-%m-%d %H:%M:%S'))
            diff_day = (to_dt-from_dt)/(3600*24)
            result['value'] = {
                'number_of_days': round(diff_day)+1
            }
            return result
        result['value'] = {
            'number_of_days': 0,
        }
        return result

    def onchange_date_to(self, cr, uid, ids, date_from, date_to):
        result = {}
        if date_from and date_to:
            from_dt = time.mktime(time.strptime(date_from,'%Y-%m-%d %H:%M:%S'))
            to_dt = time.mktime(time.strptime(date_to,'%Y-%m-%d %H:%M:%S'))
            diff_day = (to_dt-from_dt)/(3600*24)
            result['value'] = {
                'number_of_days': round(diff_day)+1
            }
            return result
        result['value'] = {
            'number_of_days': 0
        }
        return result

hr_holidays_line()

class hr_holidays(osv.osv):
    _inherit = 'hr.holidays'
    _description = 'hr.holidays'
    _columns = {
        'date_from' : fields.datetime('Start Date', readonly=False, states={'draft':[('readonly',False)]}),
        'date_to' : fields.datetime('End Date', readonly=False, states={'draft':[('readonly',False)]}),
        'holiday_line': fields.one2many('hr.holidays.line', 'holiday_id', 'Holidays Line'),
        'holiday_status_id' : fields.many2one("hr.holidays.status", "Leave Type", required=False,readonly=False, states={'draft':[('readonly',False)]}),
                }

    def check_holidays(self, cr, uid, ids):
        for record in self.browse(cr, uid, ids):
            if not record.number_of_days:
                raise osv.except_osv(_('Warning!'),_('Wrong leave definition.'))
            if record.holiday_type=='employee' and record.employee_id:
                for i in record.holiday_line:
                    leave_asked = -(i.number_of_days)
#                leave_asked = record.number_of_days
                    if leave_asked < 0.00:
                        if not i.holiday_status_id.limit:
                            leaves_rest = self.pool.get('hr.holidays.status').get_days(cr, uid, [i.holiday_status_id.id], record.employee_id.id, False)[i.holiday_status_id.id]['remaining_leaves']
                            if leaves_rest < -(leave_asked):
                                raise osv.except_osv(_('Warning!'),_('You Cannot Validate leaves while available leaves are less than asked leaves for %s' %(i.holiday_status_id.name)))
            elif record.holiday_type=='category' and record.category_id:
#                leave_asked = record.number_of_days
                for i in record.holiday_line:
                    leave_asked = -(i.number_of_days)
                    if leave_asked < 0.00:
                        if not i.holiday_status_id.limit:
                            leaves_rest = self.pool.get('hr.holidays.status').get_days_cat(cr, uid, [i.holiday_status_id.id], record.category_id.id, False)[i.holiday_status_id.id]['remaining_leaves']
                            if leaves_rest < -(leave_asked):
                                raise osv.except_osv(_('Warning!'),_('You Cannot Validate leaves while available leaves are less than asked leaves for %s'%(i.holiday_status_id.name)))
            else:# This condition will never meet!! # check me
                for i in record.holiday_line:
                    holiday_ids = []
                    vals = {
                        'name' : record.name,
                        'holiday_status_id' : i.holiday_status_id.id,
                        'state': 'draft',
                        'date_from' : i.date_from,
                        'date_to' : i.date_to,
                        'notes' : record.notes,
                        'number_of_days': i.number_of_days,
                        'number_of_days_temp': i.number_of_days,
                        'type': record.type,
                        'allocation_type': record.allocation_type,
                        'parent_id': record.id,
                    }
                    employee_ids = self.pool.get('hr.employee').search(cr, uid, [])
                    for employee in employee_ids:
                        vals['employee_id'] = employee
                        user_id = self.pool.get('hr.employee').search(cr, uid, [('user_id','=',uid)])
                        if user_id:
                            vals['user_id'] = user_id[0]
                        holiday_ids.append(self.create(cr, uid, vals, context={}))
                    self.holidays_confirm(cr, uid, holiday_ids)
                    self.holidays_validate(cr, uid, holiday_ids)

            #if record.holiday_status_id.categ_id and record.date_from and record.date_to and record.employee_id:
            for i in record.holiday_line:
                if i.holiday_status_id.categ_id and i.date_from and i.date_to:
                    vals={}
                    vals['name']=record.name
                    vals['categ_id']=i.holiday_status_id.categ_id.id
                    epoch_c = time.mktime(time.strptime(i.date_to,'%Y-%m-%d %H:%M:%S'))
                    epoch_d = time.mktime(time.strptime(i.date_from,'%Y-%m-%d %H:%M:%S'))
                    diff_day = (epoch_c - epoch_d)/(3600*24)
                    vals['duration'] = (diff_day) * 8
                    vals['note'] = record.notes
    #                vals['user_id'] = record.user_id.id
                    vals['date'] = i.date_from
                    if record.holiday_type=='employee':
                        vals['user_id'] = record.user_id.id
                    case_id = self.pool.get('crm.meeting').create(cr,uid,vals)
                    self.write(cr, uid, ids, {'case_id':case_id})
        return True

    def holidays_validate(self, cr, uid, ids, *args):
        self.check_holidays(cr, uid, ids)
        vals = {
            'state':'validate',
        }
        ids2 = self.pool.get('hr.employee').search(cr, uid, [('user_id','=', uid)])
        if ids2:
            vals['manager_id'] = ids2[0]
        else:
            raise osv.except_osv(_('Warning !'),_('No user related to the selected employee.'))
        self.write(cr, uid, ids, vals)
        for record in self.browse(cr, uid, ids):
            for i in record.holiday_line:
                if record.holiday_type=='employee' and record.type=='remove':
                    vals= {
                       'name':record.name,
                       'date_from':i.date_from,
                       'date_to':i.date_to,
                       'calendar_id':record.employee_id.calendar_id.id,
                       'company_id':record.employee_id.company_id.id,
                       'resource_id':record.employee_id.resource_id.id
                         }
                    self.pool.get('resource.calendar.leaves').create(cr, uid, vals)
        return True

    def holidays_confirm(self, cr, uid, ids, *args):
        for record in self.browse(cr, uid, ids):
            user_id = False
#            leave_asked = record.number_of_days_temp
            if record.holiday_type=='employee' and record.type == 'remove':
#                if record.employee_id and not record.holiday_status_id.limit:
                    if record.employee_id:
                        for i in record.holiday_line:
                            leave_asked = i.number_of_days
                            leaves_rest = self.pool.get('hr.holidays.status').get_days( cr, uid, [i.holiday_status_id.id], record.employee_id.id, False)[i.holiday_status_id.id]['remaining_leaves']
                            if leaves_rest < leave_asked and not i.holiday_status_id.limit:
                                raise osv.except_osv(_('Warning!'),_('You cannot validate leaves for %s while available leaves are less than asked leaves for %s' %(record.employee_id.name, i.holiday_status_id.name)))
                    nb = -(record.number_of_days_temp)
            elif record.holiday_type=='category' and record.type == 'remove':
#                if record.category_id and not record.holiday_status_id.limit:
                if record.category_id:
                    for j in record.holiday_line:
                        leave_asked = i.number_of_days
                        leaves_rest = self.pool.get('hr.holidays.status').get_days_cat( cr, uid, [j.holiday_status_id.id], record.category_id.id, False)[j.holiday_status_id.id]['remaining_leaves']
                        if leaves_rest < leave_asked and not i.holiday_status_id.limit:
                            raise osv.except_osv(_('Warning!'),_('You cannot validate leaves for %s while available leaves are less than asked leaves for %s' %(record.category_id.name, j.holiday_status_id.name)))
                nb = -(record.number_of_days_temp)
            else:
                nb = record.number_of_days_temp

            if record.holiday_type=='employee' and record.employee_id:
                user_id = record.employee_id.user_id and record.employee_id.user_id.id or uid


            self.write(cr, uid, [record.id], {
                'state':'confirm',
                'number_of_days': nb,
                'user_id': user_id
            })
        return True

    def create(self, cr, uid, vals, context=None):
        days = 0.0
        if context is None:
            context = {}
        if 'holiday_line' in vals:
            for i in vals['holiday_line']:
                days += i[2]['number_of_days']
            vals['number_of_days_temp'] = days
        return super(hr_holidays, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        days = 0.0
        if context is None:
            context = {}
        res = super(hr_holidays, self).write(cr, uid, ids, vals, context=context)
        if 'holiday_line' in vals and vals['holiday_line']:
            for i in self.browse(cr, uid, ids)[0].holiday_line:
                    days += i.number_of_days
            cr.execute('update hr_holidays set number_of_days_temp=%s'%(days,))
        return res

hr_holidays()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: