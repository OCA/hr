# Copyright (C) 2025 - Today: GRAP (https://www.grap.coop)
# @author: Quentin DUPONT
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Product Domain on Purchase UoM + HR expense - Glue module",
    "version": "16.0.1.0.0",
    "category": "HR",
    "maintainers": ["quentinDupont"],
    "author": "GRAP, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/hr",
    "license": "AGPL-3",
    "depends": [
        "hr_expense",
        "product_uom_po_domain",
    ],
    "data": [
        "views/view_product_product.xml",
    ],
    "auto_install": True,
}
