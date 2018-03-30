# ©  2015 2011,2013 Michael Telahun Makonnen <mmakonnen@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'HR Public Holidays',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Human Resources',
    'author': "Michael Telahun Makonnen <mmakonnen@gmail.com>, "
              "Odoo Community Association (OCA)",
    'summary': "Manage Public Holidays",
    'website': 'https://github.com/OCA/hr',
    'depends': [
        'hr_holidays',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_public_holidays_view.xml',
        'views/hr_holidays_status_views.xml',
        'report/hr_holidays_leaves_report_views.xml',
        'report/hr_holidays_templates.xml',
        'report/hr_holidays_views.xml',
        'views/hr_holidays_views.xml',
        'wizards/public_holidays_next_year_wizard.xml',
    ],
    'installable': True,
}
