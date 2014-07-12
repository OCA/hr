# -*- coding:utf-8 -*-
#
#
#    Copyright (C) 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
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
#

from openerp.osv import fields, orm
from openerp.tools.translate import _

import logging
_l = logging.getLogger(__name__)


class hr_job(orm.Model):

    _name = 'hr.job'
    _inherit = 'hr.job'

    def _get_all_child_ids(self, cr, uid, ids, field_name, arg, context=None):
        result = dict.fromkeys(ids)
        for i in ids:
            result[i] = self.search(
                cr, uid, [('parent_id', 'child_of', i)], context=context)

        return result

    _columns = {
        'department_manager': fields.boolean('Department Manager'),
        'parent_id': fields.many2one('hr.job', 'Immediate Superior', ondelete='cascade'),
        'child_ids': fields.one2many('hr.job', 'parent_id', 'Immediate Subordinates'),
        'all_child_ids': fields.function(_get_all_child_ids, type='many2many', relation='hr.job'),
        'parent_left': fields.integer('Left Parent', select=1),
        'parent_right': fields.integer('Right Parent', select=1),
    }

    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'name'
    _order = 'parent_left'

    def _check_recursion(self, cr, uid, ids, context=None):

        # Copied from product.category
        # This is a brute-force approach to the problem, but should be good enough.
        #
        level = 100
        while len(ids):
            cr.execute(
                'select distinct parent_id from hr_job where id IN %s', (tuple(ids),))
            ids = filter(None, map(lambda x: x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    _constraints = [
        (_check_recursion,
         _('Error!\nYou cannot create recursive jobs.'), ['parent_id']),
    ]

    def write(self, cr, uid, ids, vals, context=None):

        res = super(hr_job, self).write(cr, uid, ids, vals, context=None)

        if isinstance(ids, (int, long)):
            ids = [ids]

        dept_obj = self.pool.get('hr.department')
        if vals.get('department_manager', False):
            for di in ids:
                job = self.browse(cr, uid, di, context=context)
                dept_id = False
                if vals.get('department_id', False):
                    dept_id = vals['department_id']
                else:
                    dept_id = job.department_id.id
                employee_id = False
                for ee in job.employee_ids:
                    employee_id = ee.id
                if employee_id:
                    dept_obj.write(
                        cr, uid, dept_id, {'manager_id': employee_id}, context=context)
        elif vals.get('department_id', False):
            for di in ids:
                job = self.browse(cr, uid, di, context=context)
                if job.department_manager:
                    employee_id = False
                    for ee in job.employee_ids:
                        employee_id = ee.id
                    dept_obj.write(cr, uid, vals['department_id'], {
                                   'manager_id': employee_id}, context=context)
        elif vals.get('parent_id', False):
            ee_obj = self.pool.get('hr.employee')
            parent_job = self.browse(
                cr, uid, vals['parent_id'], context=context)
            parent_id = False
            for ee in parent_job.employee_ids:
                parent_id = ee.id
            for job in self.browse(cr, uid, ids, context=context):
                for ee in job.employee_ids:
                    ee_obj.write(
                        cr, uid, ee.id, {'parent_id': parent_id}, context=context)

        return res


class hr_contract(orm.Model):

    _name = 'hr.contract'
    _inherit = 'hr.contract'

    def create(self, cr, uid, vals, context=None):

        res = super(hr_contract, self).create(cr, uid, vals, context=context)

        if not vals.get('job_id', False):
            return res

        ee_obj = self.pool.get('hr.employee')
        job = self.pool.get('hr.job').browse(
            cr, uid, vals['job_id'], context=context)

        # Write the employee's manager
        if job and job.parent_id:
            parent_id = False
            for ee in job.parent_id.employee_ids:
                parent_id = ee.id
            if parent_id and vals.get('employee_id'):
                ee_obj.write(
                    cr, uid, vals['employee_id'], {'parent_id': parent_id},
                    context=context)

        # Write any employees with jobs that are immediate descendants of this
        # job
        if job:
            job_child_ids = []
            [job_child_ids.append(child.id) for child in job.child_ids]
            if len(job_child_ids) > 0:
                ee_ids = ee_obj.search(
                    cr, uid, [('job_id', 'in', job_child_ids)])
                if len(ee_ids) > 0:
                    parent_id = False
                    for ee in job.employee_ids:
                        parent_id = ee.id
                    if parent_id:
                        ee_obj.write(
                            cr, uid, ee_ids, {'parent_id': parent_id}, context=context)

        return res

    def write(self, cr, uid, ids, vals, context=None):

        res = super(hr_contract, self).write(
            cr, uid, ids, vals, context=context)

        if not vals.get('job_id', False):
            return res

        if isinstance(ids, (int, long)):
            ids = [ids]

        ee_obj = self.pool.get('hr.employee')

        job = self.pool.get('hr.job').browse(
            cr, uid, vals['job_id'], context=context)

        # Write the employee's manager
        if job and job.parent_id:
            parent_id = False
            for ee in job.parent_id.employee_ids:
                parent_id = ee.id
            if parent_id:
                for contract in self.browse(cr, uid, ids, context=context):
                    ee_obj.write(cr, uid, contract.employee_id.id, {
                                 'parent_id': parent_id}, context=context)

        # Write any employees with jobs that are immediate descendants of this
        # job
        if job:
            job_child_ids = []
            [job_child_ids.append(child.id) for child in job.child_ids]
            if len(job_child_ids) > 0:
                ee_ids = ee_obj.search(
                    cr, uid, [('job_id', 'in', job_child_ids),
                              ('active', '=', True)])
                if len(ee_ids) > 0:
                    parent_id = False
                    for ee in job.employee_ids:
                        parent_id = ee.id
                    if parent_id:
                        ee_obj.write(
                            cr, uid, ee_ids, {'parent_id': parent_id}, context=context)

        return res
