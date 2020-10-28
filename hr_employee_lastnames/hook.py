from odoo import SUPERUSER_ID
from odoo.api import Environment


def post_init_hook(cr, _):
    # This SQL statement is necessary to call _install_employee_lastnames() and
    # set name fields correctly.
    #
    # After the installation, previously the dependency hr_employee_firstname
    # splitting the name into two parts: firstname and lastname, so for this
    # module to be able to process the new field lastmane2 it is necessary to
    # reset the values to empty to be able to correctly set the three fields
    # (firstname, lastname and lastname2).
    #
    # For example:
    #  After install hr_employee_fisrtname and before install hr_employee_lastnames:
    #     name = 'John Peterson Clinton'
    #     firstname = 'John'
    #     lastname = 'Peterson Clinton'
    #
    #  After install hr_employee_lastnames:
    #     name = 'John Peterson Clinton'
    #     firstname = 'John'
    #     lastname = 'Peterson'
    #     lastname2 = 'Clinton'
    cr.execute("UPDATE hr_employee SET firstname = NULL, lastname = NULL")
    env = Environment(cr, SUPERUSER_ID, {})
    env["hr.employee"]._install_employee_lastnames()
    env["ir.config_parameter"].sudo().set_param("employee_names_order", "first_last")
