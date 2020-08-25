# Copyright 2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    @api.model
    def _get_employee_full_name_middle_name(self, firstname, lastname, middle_name):
        """Compute the 'name' field according to split data.
        You can override this method to change the order of lastname and
        firstname the computed name"""
        order = self.env["res.partner"]._get_names_order()
        if order == "last_first_comma":
            res = ", ".join(p for p in (lastname, middle_name, firstname) if p)
        elif order == "first_last":
            res = " ".join(p for p in (firstname, middle_name, lastname) if p)
        else:
            res = " ".join(p for p in (lastname, middle_name, firstname) if p)
        return self.env["res.partner"]._get_whitespace_cleaned_name(res)

    @api.onchange("firstname", "lastname", "middle_name")
    def _onchange_firstname_lastname(self):
        if not self.middle_name:
            return super()._onchange_firstname_lastname()
        if self.firstname or self.lastname:
            self.name = self._get_employee_full_name_middle_name(
                self.firstname, self.lastname, self.middle_name
            )

    def _prepare_vals_on_create_firstname_lastname(self, vals):
        res = super()._prepare_vals_on_create_firstname_lastname(vals)
        if vals.get("middle_name"):
            if vals.get("firstname") or vals.get("lastname"):
                vals["name"] = self._get_employee_full_name_middle_name(
                    vals.get("firstname"), vals.get("lastname"), vals.get("middle_name")
                )
        return res

    def _prepare_vals_on_write_firstname_lastname(self, vals):
        res = super()._prepare_vals_on_write_firstname_lastname(vals)
        if "firstname" in vals or "lastname" in vals or "middle_name" in vals:
            if "lastname" in vals:
                lastname = vals.get("lastname")
            else:
                lastname = self.lastname
            if "firstname" in vals:
                firstname = vals.get("firstname")
            else:
                firstname = self.firstname
            if "middle_name" in vals:
                middle_name = vals.get("middle_name")
            else:
                middle_name = self.middle_name
            vals["name"] = self._get_employee_full_name_middle_name(
                firstname, lastname, middle_name
            )
        return res
