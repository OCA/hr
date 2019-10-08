# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "HR Holidays Notify Employee Manager",
    "summary": "Notify employee's manager by mail on Leave Requests "
               "creation.",
    "version": "12.0.1.0.0",
    "category": "Human Resources",
    "website": "https://github.com/OCA/hr",
    "author": "Eficent, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "hr_holidays_settings"
    ],
    "data": [
        'views/res_config_settings_view.xml'
    ],
}
