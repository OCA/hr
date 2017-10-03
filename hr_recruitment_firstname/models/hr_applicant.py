# -*- coding: utf-8 -*-
#
##############################################################################
#
#    Authors: Adrien Peiffer
#    Copyright (c) 2015 Acsone SA/NV (http://www.acsone.eu)
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

from openerp import models, fields, api


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    partner_name = fields.Char(string="Applicant's Lastname")
    partner_firstname = fields.Char(string="Applicant's Firstname")

    @api.multi
    def create_employee_from_applicant(self):
        res = super(HrApplicant, self).create_employee_from_applicant()
        for applicant in self:
            if applicant.emp_id.id:
                if applicant.partner_firstname and applicant.partner_name:
                    applicant.emp_id.lastname = applicant.partner_name
                    applicant.emp_id.firstname = applicant.partner_firstname
            elif applicant.partner_id:
                applicant.emp_id.lastname =\
                    applicant.partner_id.lastname
                applicant.emp_id.firstname =\
                    applicant.partner_id.firstname
        return res
