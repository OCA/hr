#-*- coding:utf-8 -*-
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

from openerp.osv import fields, osv
from openerp.tools.translate import _

import logging
_l = logging.getLogger(__name__)


class hr_job(osv.Model):

    _inherit = 'hr.job'

    _columns = {
        'category_ids': fields.many2many('hr.employee.category', 'job_category_rel', 'job_id',
                                         'category_id', 'Associated Tags'),
    }


class hr_contract(osv.Model):

    _name = 'hr.contract'
    _inherit = 'hr.contract'

    def _remove_tags(self, cr, uid, employee_id, job_id, context=None):

        if not employee_id or not job_id:
            return

        ee_obj = self.pool.get('hr.employee')
        eedata = ee_obj.read(
            cr, uid, employee_id, ['category_ids'], context=context)
        job = self.pool.get('hr.job').browse(cr, uid, job_id, context=context)
        _l.warning('remv: eedata: %s', eedata)
        for tag in job.category_ids:
            if tag.id in eedata['category_ids']:
                ee_obj.write(cr, uid, employee_id, {
                             'category_ids': [(3, tag.id)]}, context=context)
        return

    def _tag_employees(self, cr, uid, employee_id, job_id, context=None):

        if not employee_id or not job_id:
            return

        ee_obj = self.pool.get('hr.employee')
        eedata = ee_obj.read(
            cr, uid, employee_id, ['category_ids'], context=context)
        job = self.pool.get('hr.job').browse(cr, uid, job_id, context=context)
        _l.warning('tag: eedata: %s', eedata)
        for tag in job.category_ids:
            _l.warning('tag: name,id: %s,%s', tag.name, tag.id)
            if tag.id not in eedata['category_ids']:
                _l.warning('tag: write()')
                ee_obj.write(cr, uid, employee_id, {
                             'category_ids': [(4, tag.id)]}, context=context)
        return

    def create(self, cr, uid, vals, context=None):

        res = super(hr_contract, self).create(cr, uid, vals, context=context)

        self._tag_employees(
            cr, uid, vals.get('employee_id', False), vals.get('job_id', False),
            context)

        return res

    def write(self, cr, uid, ids, vals, context=None):

        if isinstance(ids, (int, long)):
            ids = [ids]

        prev_data = self.read(cr, uid, ids, ['job_id'], context=context)
        _l.warning('prev_data: %s', prev_data)

        res = super(hr_contract, self).write(
            cr, uid, ids, vals, context=context)

        # Go through each record and delete tags associated with the previous job, then
        # add the tags of the new job.
        #
        for contract in self.browse(cr, uid, ids, context=context):
            for data in prev_data:
                if data['id'] == contract.id:
                    if not vals.get('job_id', False) or data['job_id'][0] != vals['job_id']:
                        prev_job_id = data.get(
                            'job_id', False) and data['job_id'][0] or False
                        _l.warning(
                            'prev Job, new job: %s, %s', prev_job_id, vals.get('job_id', False))
                        self._remove_tags(
                            cr, uid, contract.employee_id.id, prev_job_id,
                            context=context)
                        if vals.get('job_id', False):
                            self._tag_employees(
                                cr, uid, contract.employee_id.id, contract.job_id.id,
                                context=context)

        return res
