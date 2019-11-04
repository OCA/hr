# -*- coding: utf-8 -*-
import logging
from odoo import models, api

logger = logging.getLogger(__name__)
can_upgrade = False
try:
    from openupgradelib import openupgrade
    can_upgrade = True
except ImportError:
    logger.warning("Install openupgradelib to upgrade module name of "
                   "hr_attendance_calendar to hr_attendance_management")
    can_upgrade = False


class Migrate(models.AbstractModel):
    _name = 'hr.attendance.calendar.migrate'

    @api.model
    def migrate(self):
        if can_upgrade:
            openupgrade.update_module_names(
                self.env.cr, [
                    ('hr_attendance_calendar', 'hr_attendance_management'),
                ],
                merge_modules=True
            )
            return True
        return False
