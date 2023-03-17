# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2020 CorporateHub (https://corporatehub.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "HR Contract Rate",
    "version": "14.0.1.0.0",
    "category": "Human Resources",
    "website": "https://github.com/OCA/hr",
    "author": "CorporateHub, " "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "summary": "Employee's contract rate and period",
    "pre_init_hook": "pre_init_hook",
    "post_init_hook": "post_init_hook",
    "depends": ["hr_contract"],
    "data": ["views/hr_contract.xml"],
}
