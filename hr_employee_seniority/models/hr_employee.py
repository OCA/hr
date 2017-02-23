# -*- coding: utf-8 -*-
# copyright 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>
# copyright 2017 Denis Leemann, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import datetime

from odoo import api, fields, models
from odoo import tools


class HrEmployee(models.Model):

    _inherit = 'hr.employee'

    initial_employment_date = fields.Date(
        string='Initial Date of Employment',
        help='Date of first employment if it was before the start of the '
             'first contract in the system.',
    )
    length_of_service = fields.Float(
        'Lenght of Service',
        compute='_compute_months_service',
    )

    @api.depends('contract_ids')
    def _compute_months_service(self):
        for employee in self:
            nb_days = 0
            DATE_FORMAT = tools.DEFAULT_SERVER_DATE_FORMAT
            date_now = fields.Date.today()

            if employee.initial_employment_date:
                from_dt = datetime.datetime.strptime(
                    employee.initial_employment_date, DATE_FORMAT)
                to_dt = datetime.datetime.strptime(date_now, DATE_FORMAT)
                nb_days += (to_dt - from_dt).days

            for contract in employee.contract_ids:
                from_dt = datetime.datetime.strptime(
                    contract.date_start, DATE_FORMAT)
                if contract.date_end:
                    to_dt = datetime.datetime.strptime(
                        contract.date_end, DATE_FORMAT)
                else:
                    to_dt = datetime.datetime.strptime(date_now, DATE_FORMAT)

                nb_days += (to_dt - from_dt).days

            # assuming in commercial calendar, one month is 30 days long
            employee.length_of_service = nb_days / 30.0
