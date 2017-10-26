# -*- coding: utf-8 -*-
# Copyright 2016-17 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Expense Move Date",
    "summary": "Move date for HR expenses journal entries",
    "version": "10.0.1.0.0",
    "category": "Human Resources",
    "website": "https://opensynergy-indonesia.com/",
    "author": "OpenSynergy Indonesia, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "hr_expense",
    ],
    "data": [
        "views/hr_expense_views.xml",
    ],
    'installable': True,
}
