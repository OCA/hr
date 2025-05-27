{
    "name": "Validate Work Entry",
    "version": "17.0.1.0.0",
    "development_status": "Alpha",
    "category": "Human Resources/Employees",
    "website": "https://github.com/OCA/hr",
    "author": "Le Filament, Odoo Community Association (OCA)",
    "maintainers": ["remi-filament"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "hr_work_entry_contract",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/hr_work_entry_security.xml",
        "data/ir_actions_server_data.xml",
        "views/hr_work_entry_views.xml",
    ],
}
