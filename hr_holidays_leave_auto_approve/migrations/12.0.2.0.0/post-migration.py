# Copyright 2019 Eficent <http://www.eficent.com>
# Copyright 2019 Tecnativa - Pedro M. Baeza
# Copyright 2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import tools

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if tools.column_exists(cr, 'hr_leave_type', 'auto_approve'):
        _logger.debug("Set Auto Approve leave type to 'Auto Validated by HR' "
                      "policy")
        cr.execute("""
            UPDATE hr_leave_type
            SET auto_approve_policy = 'hr'
            WHERE auto_approve
            """)
