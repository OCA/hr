# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Hr Contract Employee Calendar Planning",
    "version": "16.0.1.0.0",
    "category": "Human Resources",
    "website": "https://github.com/OCA/hr",
    "author": "cibex,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "auto_install": True,
    "depends": ["hr_contract", "hr_employee_calendar_planning"],
    "data": ["views/contract.xml"],
    "post_init_hook": "post_init_hook",
}
