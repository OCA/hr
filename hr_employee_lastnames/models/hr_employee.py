import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.hr_employee_firstname.models.hr_employee import UPDATE_PARTNER_FIELDS

_logger = logging.getLogger(__name__)

UPDATE_PARTNER_FIELDS += ["lastname2"]


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    firstname = fields.Char("First name")
    lastname = fields.Char("Last name")
    lastname2 = fields.Char("Second last name")

    @api.model
    def _get_name_lastnames(self, lastname, firstname, lastname2=None):
        return self.env["res.partner"]._get_computed_name(
            lastname, firstname, lastname2
        )

    def _prepare_vals_on_create_firstname_lastname(self, vals):
        values = vals.copy()
        res = super(HrEmployee, self)._prepare_vals_on_create_firstname_lastname(values)
        if any([field in vals for field in ("firstname", "lastname", "lastname2")]):
            vals["name"] = self._get_name_lastnames(
                vals.get("lastname"), vals.get("firstname"), vals.get("lastname2")
            )
        elif vals.get("name"):
            name_splitted = self.split_name(vals["name"])
            vals["firstname"] = name_splitted["firstname"]
            vals["lastname"] = name_splitted["lastname"]
            vals["lastname2"] = name_splitted["lastname2"]
        else:
            raise UserError(_("No name set."))
        return res

    def _prepare_vals_on_write_firstname_lastname(self, vals):
        values = vals.copy()
        res = super(HrEmployee, self)._prepare_vals_on_write_firstname_lastname(values)
        if any([field in vals for field in ("firstname", "lastname", "lastname2")]):
            if "lastname" in vals:
                lastname = vals["lastname"]
            else:
                lastname = self.lastname
            if "firstname" in vals:
                firstname = vals["firstname"]
            else:
                firstname = self.firstname
            if "lastname2" in vals:
                lastname2 = vals["lastname2"]
            else:
                lastname2 = self.lastname2
            vals["name"] = self._get_name_lastnames(lastname, firstname, lastname2)
        elif vals.get("name"):
            name_splitted = self.split_name(vals["name"])
            vals["lastname"] = name_splitted["lastname"]
            vals["firstname"] = name_splitted["firstname"]
            vals["lastname2"] = name_splitted["lastname2"]
        return res

    def _update_partner_firstname(self):
        for employee in self:
            partners = employee.mapped("user_id.partner_id")
            partners |= employee.mapped("address_home_id")
            partners.write(
                {
                    "firstname": employee.firstname,
                    "lastname": employee.lastname,
                    "lastname2": employee.lastname2,
                }
            )

    def _inverse_name(self):
        """Try to revert the effect of :method:`._compute_name`."""
        for record in self:
            parts = self.env["res.partner"]._get_inverse_name(record.name)
            record.write(
                {
                    "lastname": parts["lastname"],
                    "firstname": parts["firstname"],
                    "lastname2": parts["lastname2"],
                }
            )

    @api.model
    def _install_employee_lastnames(self):
        """Save names correctly in the database.
        Before installing the module, field ``name`` contains all full names.
        When installing it, this method parses those names and saves them
        correctly into the database. This can be called later too if needed.
        """
        # Find records with empty firstname and lastnames
        records = self.search([("firstname", "=", False), ("lastname", "=", False)])

        # Force calculations there
        records._inverse_name()
        _logger.info("%d employees updated installing module.", len(records))

    @api.onchange("firstname", "lastname", "lastname2")
    def _onchange_firstname_lastname(self):
        if self.firstname or self.lastname or self.lastname2:
            self.name = self._get_name_lastnames(
                self.lastname, self.firstname, self.lastname2
            )
