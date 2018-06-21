# copyright 2013 Savoir-faire Linux (<http://www.savoirfairelinux.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Employee Phone Extension',
    'version': '11.0.1.0.0',
    'category': 'Human Resources',
    'author': "Savoir-faire Linux,Odoo Community Association (OCA)",
    'website': "https://github.com/oca/hr",
    'license': 'AGPL-3',
    'depends': ['hr'],
    'data': [
        'views/hr_employee_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
