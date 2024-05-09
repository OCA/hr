# Copyright 2011, 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>
# Copyright 2016 OpenSynergy Indonesia
# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import random
import string

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    """Implement company wide unique identification number."""

    _inherit = "hr.employee"

    employee_number = fields.Char(copy=False)

    _sql_constraints = [
        (
            "employee_number_uniq",
            "unique(employee_number)",
            "The Employee Number must be unique across the company(s).",
        ),
    ]

    @api.model
    def _generate_employee_number(self):
        """Generate a random employee number"""
        company = self.env.user.company_id

        steps = 0
        for _retry in range(50):
            employee_id = False
            if company.employee_id_gen_method == "sequence":
                if not company.employee_id_sequence:
                    _logger.warning("No sequence configured for employee ID generation")
                    return employee_id
                employee_id = company.employee_id_sequence.next_by_id()
            elif company.employee_id_gen_method == "random":
                employee_id_random_digits = company.employee_id_random_digits
                rnd = random.SystemRandom()
                employee_id = "".join(
                    rnd.choice(string.digits) for x in range(employee_id_random_digits)
                )

            if self.search_count([("employee_number", "=", employee_id)]):
                steps += 1
                continue

            return employee_id

        raise UserError(
            _("Unable to generate unique Employee ID in %d steps.") % (steps,)
        )

    @api.model
    def create(self, vals):
        if not vals.get("employee_number"):
            vals["employee_number"] = self._generate_employee_number()
        return super(HrEmployee, self).create(vals)

    def name_get(self):
        res = super().name_get()
        res = []
        for emp in self:
            name = emp.name
            if emp.employee_number:
                name = "[" + str(emp.employee_number) + "] " + str(name)
            res.append((emp.id, name))
        return res

    @api.model
    def _name_search(self, name="", args=None, operator="ilike", limit=100):
        args = args if args is not None else []
        args += ["|", ("name", operator, name), ("employee_number", operator, name)]
        empl_ids = self.search(args, limit=limit)
        return empl_ids.name_get()
