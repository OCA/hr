# Copyright (C) 2017-Today: Odoo Community Association (OCA)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HrEmployeeLanguage(models.Model):
    _name = "hr.employee.language"
    _description = "HR Employee Language"

    def _get_selection(self):
        """
        generate language selection from available on db
        """
        selection = []
        for lang in self.env["res.lang"].search([("active", "in", (True, False))]):
            selection.append((lang.code, lang.name))
        return selection

    name = fields.Selection(_get_selection, string="Language", required=True)
    description = fields.Char()
    employee_id = fields.Many2one("hr.employee", string="Employee", required=True)
    can_read = fields.Boolean(string="Read", default=True)
    can_write = fields.Boolean(string="Write", default=True)
    can_speak = fields.Boolean(string="Speak", default=True)
    can_listen = fields.Boolean(string="Listen", default=True)

    def _compute_display_name(self):
        """
        redefine record display_name to show languages name instead languages code
        """
        for record in self:
            lang = self.env["res.lang"].search(
                [("code", "=", record.name), ("active", "in", (True, False))], limit=1
            )
            record.display_name = lang.name if lang.name else record.name
