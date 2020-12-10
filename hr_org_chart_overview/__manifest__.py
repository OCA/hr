# Copyright 2020 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "HR Org Chart Overview",
    "version": "13.0.1.1.1",
    "category": "Human Resources",
    "website": "https://github.com/OCA/hr",
    "author": "ForgeFlow S.L., Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "summary": "Organizational Chart Overview",
    "depends": ["hr"],
    "data": ["views/hr_org_chart_overview_templates.xml", "views/hr_views.xml"],
    "qweb": ["static/src/xml/hr_org_chart_overview.xml"],
}
