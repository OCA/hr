# Copyright 2011, 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>
# Copyright 2016 OpenSynergy Indonesia
# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
import random
import string

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

MAX_RETRY_ATTEMPTS = 50


class HrEmployee(models.Model):
    """Implement company wide unique identification number."""

    _inherit = "hr.employee"

    identification_id = fields.Char(string="Identification No", copy=False)

    _sql_constraints = [
        (
            "identification_id_uniq",
            "unique(identification_id)",
            "The Employee Number must be unique across the company(s).",
        )
    ]

    @api.model
    def _generate_identification_id(self):
        """Generate a random employee identification number"""
        company = self.env.user.company_id

        for _retry in range(MAX_RETRY_ATTEMPTS):
            identification_num = False
            if company.employee_id_gen_method == "sequence":
                if not company.employee_id_sequence:
                    _logger.warning("No sequence configured for employee ID generation")
                    return identification_num
                identification_num = company.employee_id_sequence.next_by_id()
            elif company.employee_id_gen_method == "random":
                employee_id_random_digits = company.employee_id_random_digits
                rnd = random.SystemRandom()
                identification_num = "".join(
                    rnd.choice(string.digits)
                    for _dummy in range(employee_id_random_digits)
                )

            if self.search_count([("identification_id", "=", identification_num)]):
                continue

            return identification_num

        raise UserError(
            _("Unable to generate unique Employee ID in %d steps.") % (_retry,)
        )

    @api.model
    def create(self, vals):
        if not vals.get("identification_id"):
            vals["identification_id"] = self._generate_identification_id()
        return super().create(vals)
