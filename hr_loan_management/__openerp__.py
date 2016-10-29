# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Employee Loan Management",
    "version": "8.0.1.0.0",
    "category": "Human Resources",
    "website": "https://opensynergy-indonesia.com/",
    "author": "OpenSynergy Indonesia, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": True,
    "installable": True,
    "depends": [
        "hr",
        "account_accountant",
        "base_action_rule",
    ],
    "data": [
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/ir_filter_data.xml",
        "data/ir_actions_server_data.xml",
        "data/base_action_rule_data.xml",
        "wizard/realize_interest_views.xml",
        "views/hr_loan_type_views.xml",
        "views/hr_loan_views.xml",
        "views/hr_employee_views.xml",
    ],
    "demo": [
        "demo/ir_sequence_demo.xml",
        "demo/account_account_demo.xml",
        "demo/account_journal_demo.xml",
        "demo/hr_loan_type_demo.xml",
    ],
}
