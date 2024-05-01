def post_init_hook(env):
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
    #  After install hr_employee_fisrtname and before install
    #  hr_employee_second_lastname:
    #     name = 'John Peterson Clinton'
    #     firstname = 'John'
    #     lastname = 'Peterson Clinton'
    #
    #  After install hr_employee_second_lastname:
    #     name = 'John Peterson Clinton'
    #     firstname = 'John'
    #     lastname = 'Peterson'
    #     lastname2 = 'Clinton'
    env.cr.execute("UPDATE hr_employee SET firstname = NULL, lastname = NULL")
    env["hr.employee"]._install_employee_lastnames()
    env["ir.config_parameter"].sudo().set_param("employee_names_order", "first_last")
