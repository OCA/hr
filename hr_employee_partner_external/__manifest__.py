# Copyright 2020 Stefano Consolaro (Ass. PNLUG - Gruppo Odoo <http://odoo.pnlug.it>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name":     "Employee external Partner",
    "summary":  "Associate an external Partner to Employee",
    "version":  "12.0.1.0.0",
    "category": "Human Resources",

    "author":   "Stefano Consolaro Associazione PNLUG - Gruppo Odoo, "
                "Odoo Community Association (OCA)",
    "website":  "https://github.com/OCA/hr",
    "license":  "AGPL-3",

    "depends": [
        'hr',
        ],
    "data": [
        'views/hr_employee.xml',
        ],
}
