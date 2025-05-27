{
    "name": "Work Entry with timesheets",
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
        "hr_timesheet",
        "hr_work_entry_contract",
        "project_timesheet_holidays",
    ],
    "data": [
        "views/hr_work_entry_view.xml",
    ],
}
