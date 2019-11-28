# Copyright 2014 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#                       Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'HR expense sequence',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Human Resources',
    'author': 'Serv. Tecnol. Avanzados - Pedro M. Baeza,'
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/hr',
    'depends': [
        'hr_expense',
    ],
    'data': [
        'data/hr_expense_data.xml',
        'views/hr_expense_expense_view.xml',
        'report/report_expense_sheet.xml',
    ],
    'installable': True,
    'post_init_hook': 'assign_old_sequences',
}
