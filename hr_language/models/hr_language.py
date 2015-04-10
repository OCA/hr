# -*- encoding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp import tools
from openerp import models, fields


class hr_language(models.Model):
    _name = 'hr.language'

    name = fields.Selection(
        tools.scan_languages(),
        string=u"Language", required=True)
    description = fields.Char(
        string=u"Description", size=64, required=True)
    employee_id = fields.Many2one(
        'hr.employee', string=u"Employee", required=True)
    can_read = fields.Boolean(u"Read", default=True, oldname='read')
    can_write = fields.Boolean(u"Write", default=True, oldname='write')
    can_speak = fields.Boolean(u"Speak", default=True, oldname='speak')


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    language_ids = fields.One2many(
        'hr.language', 'employee_id', u"Languages")
