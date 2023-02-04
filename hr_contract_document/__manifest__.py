# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2020-2022 CorporateHub (https://corporatehub.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "HR Contract Document",
    "version": "14.0.1.0.1",
    "category": "Human Resources",
    "website": "https://github.com/OCA/hr",
    "author": "CorporateHub, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "summary": "Documents attached to the contact",
    "depends": ["hr_contract"],
    "data": ["views/hr_contract.xml", "views/ir_attachment.xml"],
}
