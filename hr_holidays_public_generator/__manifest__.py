# Copyright 2018 elego Software Solutions GmbH - Yu Weng
# Copyright 2018 initOS GmbH - Nikolina Todorova
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": 'HR Holidays Public Generator',
    "version": '11.0.1.0.0',
    "license": "AGPL-3",
    "category": "Human Resources",
    "author": "Yu Weng <yweng@elegosoft.com>, "
              "Nikolina Todorova <nikolina.todorova@initos.com>, "
              "Odoo Community Association (OCA)",
    "description": """

HR Holidays Public Generator
=================================================
This module is used as a template and have to be
used with real implementation module.

Functions:

1. Container Wizard for Generating Public Holidays.
2. Improves onchange event to calculate public holidays

""",
    "website": "https://github.com/OCA/hr",
    "depends": [
        "l10n_de_country_states",
        "hr",
        "hr_holidays",
        "hr_holidays_public",
    ],
    "data": [
        "wizard/hr_holidays_public_generator_view.xml",
        "views/hr_holidays_public_view.xml",
    ],
    "installable": True,
    "auto_install": False,
}
