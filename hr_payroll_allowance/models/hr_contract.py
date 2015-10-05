# -*- encoding: utf-8 -*-

from lxml import etree
from dateutil.rrule import rrule, YEARLY
from datetime import datetime, timedelta, date, time

from openerp import models, fields, api, _, SUPERUSER_ID
from openerp.tools import to_xml
from openerp import tools
import openerp.addons.decimal_precision as dp
from openerp.osv.orm import setup_modifiers

class hr_contract(models.Model):
    _inherit = 'hr.contract'
    
    @api.multi
    def alw_amount_python_compute(self, slip, code):
        self.ensure_one()
        contract = self[0]
        employee = contract.employee_id
        alw_obj = self.env['hr.payroll.allowance']
        allowances = alw_obj.search([('code' , '=', code)])
        
        if not len(allowances):
            raise Warning('Allowance Category with code %s was not found' 
                          %(code))
        alw = allowances[0]        
        contract_field_name = 'x_' + alw.code.lower() + '_amount'
        # default unit and units.. this case matches what we expect if this 
        # allowance is being paid at every slip
        unit = 1
        unit_amount = getattr(contract, contract_field_name)
        if alw.interval == 'yearly':
            dtCmpStart = fields.Date.from_string(slip.date_from)
            dtCmpEnd = fields.Date.from_string(slip.date_to)
            dtEmpStart = fields.Date.from_string(employee.date_start)

            if alw.yearly_payment_strategy == 'anniversary':
                # if we should pay on anniversary and if this is the employee
                # anniversary then let's multiply the amount by 12...
                # we are assuming that the monthly amount is what is recorded
                # on the contract
                employee = employee.with_context\
                (date_now=fields.Date.to_string(dtCmpEnd))
                if employee.length_of_service > 12.0:              
                    rr = rrule(YEARLY, dtstart=(dtEmpStart + timedelta(days=1)))
                    recurringDates = rr.between(
                            datetime.combine(dtCmpStart, time.min), 
                            datetime.combine(dtCmpEnd, time.max), 
                            inc=True)                    
                    if len(recurringDates):
                        unit = 12
                    else:
                        unit = 0.0
                        unit_amount = 0.0  
            elif alw.yearly_payment_strategy == 'yearly':
                if dtCmpStart.month == 1:
                    # we are paying at the start of the year and we happen to 
                    # be in the firstg month
                    unit = 12
                else: 
                    if dtEmpStart >= dtCmpStart and dtEmpStart < dtCmpEnd and \
                    alw.yearly_payment_prorate:
                    # employee is just joining and we are being asked to prorate
                    # employee's pay over the remaining month in the year
                        unit = 12 - dtCmpStart.month + 1  
                    else:
                        unit = 0.0
                        unit_amount = 0.0   
        return unit_amount * unit
    
    @api.multi
    def alw_condition_python(self, slip, code):
        self.ensure_one()
        contract = self[0]
        employee = contract.employee_id
        alw_obj = self.env['hr.payroll.allowance']
        allowances = alw_obj.search([('code' , '=', code)])
        
        if not len(allowances):
            raise Warning('Allowance Category with code %s was not found' 
                          %(code))
        alw = allowances[0]
        if alw.interval == 'each':
            '''
            if this allowance is being paid each month then it is clearly
            simple, let's return True
            '''
            return True
        elif alw.interval == 'yearly':
            dtCmpStart = fields.Date.from_string(slip.date_from)
            dtCmpEnd = fields.Date.from_string(slip.date_to)
            dtEmpStart = fields.Date.from_string(employee.date_start)
            if alw.yearly_payment_strategy == 'anniversary':
                '''
                we pay whenever it is the anniversary of employees
                '''
                employee = employee.with_context\
                (date_now=fields.Date.to_string(dtCmpEnd))
                if employee.length_of_service > 12.0:              
                    rr = rrule(YEARLY, dtstart=(dtEmpStart + timedelta(days=1)))
                    recurringDates = rr.between(
                            datetime.combine(dtCmpStart, time.min), 
                            datetime.combine(dtCmpEnd, time.max), 
                            inc=True)                    
                    if len(recurringDates):
                        return True
                    else:
                        return False
            elif alw.yearly_payment_strategy == 'yearly':
                if dtCmpStart.month == 1: # we pay at the start of the year
                    return True
                elif alw.yearly_payment_prorate: 
                    # not start of the year but we prorate because we are being
                    # asked to
                    return True  
        return False
    
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        res = super(hr_contract, self).fields_view_get(view_id=view_id, \
                                     view_type=view_type, toolbar=toolbar,
                                     submenu=False)
        
        if view_type != 'form':
            return res
        
        allowance_obj = self.env['hr.payroll.allowance']
        allowances = allowance_obj.search(([('company_id', '=', 
                                             self.env.user.company_id.id),
                                            ('active', '=', True)]),
                                          order='sequence DESC')
        
        if len(allowances) == 0:
            return res
        
        doc = etree.XML(res['arch'])
        nodes = doc.xpath("//field[@name='wage']")
        node = nodes[0]
       
        for allowance in allowances:
            field_name = 'x_' + allowance.code.lower() + '_amount'
            child_str = "<field name='%s'/>" % (field_name)
            child = etree.fromstring(child_str)
            node.addnext(child)
            field_data = {
                            'digits': (16, 2), 
                            'string': allowance.name, 
                            'views': {}, 
                            'readonly': False, 
                            'type': 'float'
                           }
            res['fields'].update({field_name : field_data})
            
            allowance_nodes = doc.xpath("//field[@name='%s']" % (field_name))
            allowance_node = allowance_nodes[0]
            setup_modifiers(allowance_node, res['fields'][field_name])            
            res['arch'] = etree.tostring(doc)
        return res