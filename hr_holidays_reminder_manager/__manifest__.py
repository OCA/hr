# Copyright (c) 2020 Hashbang (<https://hashbang.fr>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "HR Holidays Reminder Manager",
    "summary": "Send reminder to HR manager by mail on Leave Requests "
               "creation and send a notify to HR manager when leave "
               "is approved.",
    "version": "12.0.1.1.0",
    "category": "Human Resources",
    "website": "https://github.com/OCA/hr",
    "author": (
        "Odoo Community Association (OCA), Hashbang"
    ),
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "hr_holidays_settings",
    ],
    "data": [
        'data/mail_data.xml',
        'views/res_config_settings_view.xml',
        'views/hr_employee.xml',
    ],
}
