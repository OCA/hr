# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2018 Compassion CH (http://www.compassion.ch)
#    @author: Eicher Stephane <seicher@compassion.ch>
#    @author: Emanuel Cino <ecino@compassion.ch>
#
#    The licence is in the file __manifest__.py
#
##############################################################################

from odoo import models, fields


class HrHolidaysStatus(models.Model):
    _inherit = 'hr.holidays.status'

    keep_due_hours = fields.Boolean(oldname='remove_from_due_hours')
