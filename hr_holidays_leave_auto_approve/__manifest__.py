# -*- coding: utf-8 -*-
# © 2016 ONESTEiN BV (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Auto Approve Leaves',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'summary': '''Leave type for auto approval of Leaves''',
    'author': 'ONESTEiN BV, Odoo Community Association (OCA)',
    'website': 'http://www.onestein.eu',
    'category': 'Human Resources',
    'depends': [
        'hr_holidays',
    ],
    'data': [
        'views/hr_holidays_status.xml',
    ],
    'installable': True,
}
