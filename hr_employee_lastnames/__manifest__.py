# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': "HR Employee First Name and Two Last Names",
    'version': '10.0.2.0.0',
    'author': "Vauxoo, "
              "Odoo Community Association (OCA)",
    'maintainer': 'Vauxoo',
    'website': 'https://github.com/OCA/hr/',
    'license': 'AGPL-3',
    'category': 'Human Resources',
    'summary': "Split Name in First Name, Father's Last Name and Mother's Last Name",
    'depends': [
        'partner_second_lastname',
        'hr_employee_firstname',
    ],
    'data': [
        'views/hr_views.xml',
    ],
    'post_init_hook': "post_init_hook",
    'demo': [],
    'test': [],
    'installable': True,
}
