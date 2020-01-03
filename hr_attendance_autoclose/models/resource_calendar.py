# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# Copyright 2019 Jesus Ramoneda <jesus.ramoneda@qubiq.es>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    attendance_maximum_hours_per_day = fields.Float(
        string='Attendance Maximum Hours Per Day',
        digits=(2, 2), default=11.0)
