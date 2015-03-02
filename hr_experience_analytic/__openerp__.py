###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

{
    "name": "Experience and Analytic Accounting",
    "version": "0.1",
    "author": "Savoir-faire Linux,Odoo Community Association (OCA)",
    "category": "Human Resources",
    "website": "http://www.savoirfairelinux.com",
    "depends": [
        "hr_experience",
        "account",
    ],
    "description": """
This module allows you to link your employee experiences with projects
or contracts.

This is useful if you want to have the same project description and metrics on
all the resumes of the employees involved in the same project or contract.

Configuration
=============

Make sure to add users to the "Analytic Accounting" group to show the analytic
account on the profesionnal experience form.

Contributors
============

* Savoir-faire Linux <support@savoirfairelinux.com>
* Maxime Chambreuil <maxime.chambreuil@savoirfairelinux.com>
    """,
    "data": [
        "hr_experience_analytic_view.xml",
    ],
    "installable": True,
}
