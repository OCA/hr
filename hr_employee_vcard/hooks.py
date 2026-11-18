def post_init_hook(env):
    """Apply the vCard defaults to companies that already existed on install.

    Field defaults only run when a company is created, so companies present
    before installing the module would otherwise have no layout nor fields.
    """
    layout = env.ref(
        "hr_employee_vcard.hr_employee_vcard_layout_modern", raise_if_not_found=False
    )
    for company in env["res.company"].search([]):
        vals = {}
        if not company.vcard_layout_id and layout:
            vals["vcard_layout_id"] = layout.id
        if not company.vcard_layout_field_ids:
            vals["vcard_layout_field_ids"] = [
                (6, 0, company._default_vcard_layout_field_ids().ids)
            ]
        if vals:
            company.write(vals)
