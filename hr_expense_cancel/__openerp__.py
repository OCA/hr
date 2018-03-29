# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L. (
# <http://www.eficent.com>).
# © 2015 Ecosoft Pvt Ltd. (# <http://www.ecosoft.co.th>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name' : 'HR Expense Cancel',
    'version' : '8.0.1.0.0',
    'author' : 'Ecosoft',
    'summary': 'Cancel HR Expense that has been posted',
    'category': 'Accounting & Finance',
    'website': 'http://www.ecosoft.co.th',
    'depends': ['hr_expense'],
    'data': [
        'views/hr_expense_view.xml',
        'views/hr_expense_workflow.xml',
    ],
    'application': True,
    'installable': True,
}
