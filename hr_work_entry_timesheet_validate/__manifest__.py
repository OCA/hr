{
    "name": "Work Entry with timesheets and validation",
    "version": "18.0.1.0.0",
    "development_status": "Alpha",
    "category": "Human Resources/Employees",
    "website": "https://github.com/OCA/hr",
    "author": "Le Filament, Odoo Community Association (OCA)",
    "maintainers": ["remi-filament"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "hr_work_entry_timesheet",
        "hr_work_entry_validate",
    ],
    "data": [
        "views/hr_work_entry_view.xml",
    ],
}
