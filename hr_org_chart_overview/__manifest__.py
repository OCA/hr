# Copyright 2020 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "HR Org Chart Overview",
    "version": "15.0.1.0.0",
    "category": "Human Resources",
    "website": "https://github.com/OCA/hr",
    "author": "ForgeFlow S.L., Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "summary": "Organizational Chart Overview",
    "depends": ["hr"],
    "data": ["views/hr_views.xml"],
    "qweb": ["static/src/xml/hr_org_chart_overview.xml"],
    "assets": {
        "web.assets_backend": [
            "/hr_org_chart_overview/static/src/js/hr_org_chart_overview.js",
            "/hr_org_chart_overview/static/src/lib/orgchart/html2canvas.min.js",
            "/hr_org_chart_overview/static/src/lib/orgchart/jspdf.min.js",
            "/hr_org_chart_overview/static/src/lib/orgchart/jquery.orgchart.js",
            "/hr_org_chart_overview/static/src/lib/orgchart/jquery.orgchart.css",
            "/hr_org_chart_overview/static/src/scss/hr_org_chart_style.scss",
        ],
        "web.assets_qweb": [
            "hr_org_chart_overview/static/src/xml/**/*",
        ],
    },
}
