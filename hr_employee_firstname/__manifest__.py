# Copyright 2010-2014 Savoir-faire Linux (<http://www.savoirfairelinux.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "HR Employee First Name, Last Name",
    "version": "14.0.3.0.0",
    "author": "Savoir-faire Linux, "
    "Fekete Mihai (Forest and Biomass Services Romania), "
    "Onestein, "
    "Odoo Community Association (OCA)",
    "maintainer": "Savoir-faire Linux",
    "website": "https://github.com/OCA/hr",
    "license": "AGPL-3",
    "category": "Human Resources",
    "summary": "Adds First Name to Employee",
    "depends": ["hr"],
    "data": ["views/hr_view.xml", "views/base_config_view.xml"],
    "post_init_hook": "post_init_hook",
    "installable": True,
}
