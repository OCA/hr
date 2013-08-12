#-*- coding:utf-8 -*-
##############################################################################
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
##############################################################################

from datetime import datetime,date

from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DATEFORMAT
from openerp.tools.translate import _

from ethiopic_calendar.ethiopic_calendar import ET_MONTHS_SELECTION, ET_DAYOFMONTH_SELECTION
from ethiopic_calendar.pycalcal import pycalcal as pcc

class new_labour(osv.Model):
    
    _name = 'hr.recruitment.labour.new'
    _description = 'Daily Labour Recruitment Form'
    
    def _get_year(self, cr, uid, context=None):
        
        res = []
        
        # Assuming employees are at least 16 years old
        year = datetime.now().year
        year -= 16
        
        # Convert to Ethiopic calendar
        pccDate = pcc.ethiopic_from_fixed(
                    pcc.fixed_from_gregorian(
                            pcc.gregorian_date(year, 1, 1)))
        year = pccDate[0]
        
        i = year
        while i > (year - 59):
            res.append((str(i), str(i)))
            i -= 1
        
        return res
    
    _columns = {
        'name': fields.char('Name', size=128),
        'ethiopic_name': fields.char('Ethiopic Name', size=512),
        'birth_date': fields.date('Birth Date'),
        'use_ethiopic_dob': fields.boolean('Use Ethiopic Birthday'),
        'etcal_dob_month': fields.selection(ET_MONTHS_SELECTION, 'Month'),
        'etcal_dob_day': fields.selection(ET_DAYOFMONTH_SELECTION, 'Day'),
        'etcal_dob_year': fields.selection(_get_year, 'Year'),
        'gender': fields.selection([('f', 'Female'),('m', 'Male')], 'Gender'),
        'id_no': fields.char('Official ID', size=32),
        'house_no': fields.char('House No.', size=8),
        'kebele': fields.char('Kebele', size=8),
        'woreda': fields.char('Subcity/Woreda', size=32),
        'city': fields.char('City', size=32),
        'state_id': fields.many2one('res.country.state', 'State'),
        'country_id': fields.many2one('res.country', 'Country'),
        'telephone': fields.char('Telephone', size=19),
        'mobile': fields.char('Mobile', size=19),
        'job_id': fields.many2one('hr.job', 'Applied Job'),
        'department_id': fields.many2one('hr.department', 'Department'),
        'education': fields.selection((
                                       ('none', 'No Education'),
                                       ('primary', 'Primary School'),
                                       ('secondary', 'Secondary School'),
                                       ('diploma', 'Diploma'),
                                       ('degree1', 'First Degree'),
                                       ('masters', 'Masters Degree'),
                                       ('phd', 'PhD'),
                                      ), 'Education'),
    }
    
    def _get_country(self, cr, uid, context=None):
        
        company_id = self.pool.get('res.company')._company_default_get(cr, uid, 'hr.applicant', context=context)
        data = self.pool.get('res.company').read(cr, uid, company_id, context=context)
        return data.get('country_id', False) and data['country_id'][0] or False
    
    _defaults = {
        'country_id': _get_country,
        'use_ethiopic_dob': True,
        'education': 'none',
    }
    
    def onchange_etdob(self, cr, uid, ids, y, m, d, context=None):
        
        res = {'value': {'birth_date': False}}
        if d and m and y:
            dob = pcc.gregorian_from_fixed(
                        pcc.fixed_from_ethiopic(
                                pcc.ethiopic_date(int(y), int(m), int(d))))
            res['value']['birth_date'] = date(year=dob[0], month=dob[1], day=dob[2]).strftime(OE_DATEFORMAT)
        return res

    def onchange_country(self, cr, uid, ids, country_id, context=None):
        
        res = {'domain': {'state_id': False}}
        if country_id:
            res['domain']['state_id'] = [('country_id', '=', country_id)]
        
        return res
            
    def onchange_job(self, cr, uid, ids, job, context=None):
        result = {}

        if job:
            job_obj = self.pool.get('hr.job')
            result['department_id'] = job_obj.browse(cr, uid, job, context=context).department_id.id
            return {'value': result}
        return {'value': {'department_id': False}}
    
    def create_applicant(self, cr, uid, ids, context=None):
        
        data = self.read(cr, uid, ids[0], context=context)
        if not data.get('name', False) or not data.get('birth_date', False) or not data.get('gender', False):
            raise osv.except_osv(_('Mandatory Fields Missing'), _('Make sure that at least the Name, Birth Date and Gender fields have been filled in.'))
        
        company_id = self.pool.get('res.company')._company_default_get(cr, uid, 'hr.applicant', context=context)
        
        hno = data.get('house_no', False) and 'House No: ' + data['house_no'] or ''
        kebele = data.get('kebele', False) and 'Kebele: ' + data['kebele'] or ''
        woreda = data.get('woreda', False) and 'Subcity/Woreda: ' + data['woreda'] or ''
        partner_vals = {
            'name': data['name'],
            'phone': data['telephone'],
            'mobile': data['mobile'],
            'street': woreda + ' ' + kebele + ' ' + hno,
            'city': data['city'],
            'country_id': data['country_id'][0],
            'state_id': data.get('state_id', False) and data['state_id'][0] or False,
            'parent_id': company_id,
            'employee': True,
            'customer': False,
        }
        partner_id = self.pool.get('res.partner').create(cr, uid, partner_vals, context=context)
        applicant_vals = {
            'name': data['name'],
            'ethiopic_name': data['ethiopic_name'],
            'partner_id': partner_id,
            'partner_phone': data['telephone'],
            'partner_mobile': data['mobile'],
            'job_id': data['job_id'][0],
            'department_id': data['department_id'][0],
            'gender': data['gender'],
            'use_ethiopic_dob': data['use_ethiopic_dob'],
            'etcal_dob_year': data['etcal_dob_year'],
            'etcal_dob_month': data['etcal_dob_month'],
            'etcal_dob_day': data['etcal_dob_day'],
            'birth_date': data['birth_date'],
            'education': data['education'],
        }
        self.pool.get('hr.applicant').create(cr, uid, applicant_vals, context=context)
        
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.recruitment.labour.new',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        }
    
    def cancel_wizard(self, cr, uid, ids, context=None):
        
        res_model, res_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'hr_recruitment', 'crm_case_categ0_act_job')
        act_window_obj = self.pool.get('ir.actions.act_window')
        dict_act_window = act_window_obj.read(cr, uid, res_id, [])
        dict_act_window['view_mode'] = 'kanban,tree,form,graph,calendar'
        return dict_act_window
