# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "HR Holiday Notify Employee Manager",
    "summary": "Notify employee's manager by mail on Leave Requests "
               "creation.",
    "version": "9.0.1.0.0",
    "category": "Human Resources",
    "website": "https://odoo-community.org/",
    "author": "Eficent, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["hr_holidays"],
    "data": ['views/res_company_view.xml'],
}
