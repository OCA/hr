# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DFORMAT
from datetime import datetime


class HrAccidentatwork(models.Model):
    _name = 'hr.accident.at.work'
    _description = 'HR Accident at work'

    employee_id = fields.Many2one(comodel_name='hr.employee', required=True,
                                  string="Employee")
    accident_address = fields.Text(string='Accident Adress')
    accident_date = fields.Datetime(string='Date', required=True)
    accident_sequence = fields.Selection(selection=[
        ('EXCEPTIONAL FREQUENCY', 'EXCEPTIONAL FREQUENCY'),
        ('REGULAR FREQUENCY', 'REGULAR FREQUENCY'),
    ], string='Frequency Type')
    accident_department = fields.Integer(string='Department', required=True)
    accident_location = fields.Char(string='Location')
    number_of_employee_involved = fields.Integer(
        string='Number of Employees Involved', default=1, required=True)
    number_of_employee_involved_acknowledge_by_social_security = \
        fields.Integer(string='Number of Employee concerned and acknowledge by'
                              ' the Social Security Authority', default=0)
    social_security_authority_decision = fields.Text(
        string='Social Security Authority Decision')
    accident_almost = fields.Boolean(string='Almost accident ?', default=False)
    accident_during_commute = fields.Boolean(string='Accident during the '
                                                    'commuting ?',
                                             default=False)
    accident_circumstances = fields.Text(string='circumstances', required=True)
    wound_description = fields.Text(string='Wound description', required=True)
    declaration_done = fields.Boolean(
        string='Declaration Done?', default=False)
    work_stoppage = fields.Boolean(string='Work Stoppage')
    work_stoppage_start_date = fields.Date(string='Work Stoppage Start Date')
    work_stoppage_end_date = fields.Date(string='Work Stoppage End Date')
    work_stoppage_duration_days = fields.Integer(
        string='Work Stoppage Duration',
        compute='_compute_duration',
        help='In Days')
    work_stoppage_duration_working_days = fields.Integer(
        string='Work Stoppage Duration in Working Days')
    back_to_work_date = fields.Date(string='Back to Work Date')
    comment = fields.Text(string='Comments')
    do_not_declare = fields.Text(string='Do not Declare')

    @api.multi
    def _compute_duration(self):
        for res in self:
            if res.work_stoppage:
                start = res.work_stoppage_start_date
                end = res.work_stoppage_end_date
                from_dt = datetime.strptime(start, OE_DFORMAT)
                to_dt = datetime.strptime(end, OE_DFORMAT)
                timedelta = to_dt - from_dt
                diff_day = int(timedelta.days + float(timedelta.seconds)/86400)
                res.work_stoppage_duration_days = diff_day
