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

from datetime import date

from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.translate import _

from pycalcal import pycalcal as pcc

ET_MONTHS_SELECTION_AM = [
    u'መስከረም', u'ጥቅምት', u'ህዳር', u'ታህሳስ', u'ጥር',
    u'የካቲት', u'መጋቢት', u'ሚያዝያ', u'ግንቦት', u'ሰኔ',
    u'ሃምሌ', u'ነሐሴ', u'ጳጉሜ', 
]

ET_MONTHS_SELECTION = [
    ('1', _('Meskerem')),
    ('2', _('Tikimt')),
    ('3', _('Hedar')),
    ('4', _('Tahsas')),
    ('5', _('Tir')),
    ('6', _('Yekatit')),
    ('7', _('Megabit')),
    ('8', _('Miazia')),
    ('9', _('Genbot')),
    ('10', _('Senie')),
    ('11', _('Hamle')),
    ('12', _('Nehassie')),
    ('13', _('Pagume')),
]

ET_DAYOFMONTH_SELECTION = [
    ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), 
    ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'), 
    ('11', '11'), ('12', '12'), ('13', '13'), ('14', '14'), ('15', '15'), 
    ('16', '16'), ('17', '17'), ('18', '18'), ('19', '19'), ('20', '20'), 
    ('21', '21'), ('22', '22'), ('23', '23'), ('24', '24'), ('25', '25'), 
    ('26', '26'), ('27', '27'), ('28', '28'), ('29', '29'), ('30', '30'), 
]

class hr_employee(osv.Model):
    
    _name = 'hr.employee'
    _inherit = 'hr.employee'
    
    _columns = {
        'use_ethiopic_dob': fields.boolean('Use Ethiopic Birthday'),
        'etcal_dob_month': fields.selection(ET_MONTHS_SELECTION, 'Month'),
        'etcal_dob_day': fields.selection(ET_DAYOFMONTH_SELECTION, 'Day'),
        'etcal_dob_year': fields.char('Year', size=4),
    }
    
    _defaults = {
        'use_ethiopic_dob': True,
    }
    
    def onchange_etdob(self, cr, uid, ids, y, m, d, context=None):
        
        res = {'value': {'birthday': False}}
        if d and m and y:
            dob = pcc.gregorian_from_fixed(
                        pcc.fixed_from_ethiopic(
                                pcc.ethiopic_date(int(y), int(m), int(d))))
            res['value']['birthday'] = date(year=dob[0], month=dob[1], day=dob[2]).strftime(DEFAULT_SERVER_DATE_FORMAT)
        return res
    
    def create(self, cr, uid, vals, context=None):
        
        if vals.get('etcal_dob_year', False) and vals.get('etcal_dob_month', False) and vals.get('etcal_dob_day', False) and not vals.get('birthday', False):
            dob = pcc.gregorian_from_fixed(
                        pcc.fixed_from_ethiopic(
                                pcc.ethiopic_date(int(vals['etcal_dob_year']), int(vals['etcal_dob_month']),
                                                  int(vals['etcal_dob_day']))))
            vals['birthday'] = date(year=dob[0], month=dob[1], day=dob[2]).strftime(DEFAULT_SERVER_DATE_FORMAT)
        
        return super(hr_employee, self).create(cr, uid, vals, context=context)
    
    def write(self, cr, uid, ids, vals, context=None):
        
        res =  super(hr_employee, self).write(cr, uid, ids, vals, context=context)
        
        y = vals.get('etcal_dob_year', False)
        m = vals.get('etcal_dob_month', False)
        d = vals.get('etcal_dob_day', False)
        
        if y or m or d:
            for i in ids:
                data = {'birthday': ''}
                rdata = self.read(cr, uid, i, ['etcal_dob_year', 'etcal_dob_month', 'etcal_dob_day'],
                                  context=context)
                if not y:
                    y = rdata['etcal_dob_year']
                if not m:
                    m = rdata['etcal_dob_month']
                if not d:
                    d = rdata['etcal_dob_day']
                dob = pcc.gregorian_from_fixed(
                            pcc.fixed_from_ethiopic(
                                    pcc.ethiopic_date(int(y), int(m), int(d))))
                data['birthday'] = date(year=dob[0], month=dob[1], day=dob[2]).strftime(DEFAULT_SERVER_DATE_FORMAT)
                
                super(hr_employee, self).write(cr, uid, i, data, context=context)
        
        return res
