# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Resource Hook",
    "summary": """
        Extends the resource with hooks to standard methods.""",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/hr",
    "depends": ["resource"],
    "post_load": "post_load_hook",
}
