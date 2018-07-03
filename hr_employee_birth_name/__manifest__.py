# copyright  2017 Denis Leemann, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Employee Birth Name',
    'version': '11.0.1.0.0',
    'category': 'Human Resources',
    'author': "Camptocamp SA,Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/hr',
    'license': 'AGPL-3',
    'depends': ['hr', ],
    'data': [
        'views/hr_employee_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
