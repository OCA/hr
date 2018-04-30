# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2018 Compassion CH (http://www.compassion.ch)
#    Releasing children from poverty in Jesus' name
#    @author: Emanuel Cino <ecino@compassion.ch>
#
#    The licence is in the file __manifest__.py
#
##############################################################################
from openupgradelib import openupgrade


def migrate(cr, version):
    if not version:
        return

    # Rename module
    openupgrade.update_module_names(
        cr, [
            ('hr_attendance_calendar', 'hr_attendance_management'),
        ]
    )

    # Rename settings
    cr.execute("""
        UPDATE ir_config_parameter
        SET key = replace(key, 'hr_attendance_calendar',
                          'hr_attendance_management')
    """)
