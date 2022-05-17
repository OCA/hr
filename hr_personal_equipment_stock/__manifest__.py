# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Hr Personal Equipment Stock",
    "summary": """
        This addon allows to integrate hr_personal_equipment_request with stock""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/hr",
    "depends": ["hr_personal_equipment_request", "stock"],
    "data": [
        "views/stock_location.xml",
        "views/stock_move.xml",
        "views/procurement_group.xml",
        "views/hr_personal_equipment.xml",
        "views/hr_personal_equipment_request.xml",
        "views/stock_picking.xml",
    ],
    "auto_install": True,
}
