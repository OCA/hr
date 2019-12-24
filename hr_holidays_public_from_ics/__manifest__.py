# Copyright © 2019 Andrei Levin <andrei.levin@didotech.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': "HR Holidays from ics",
    'version': '12.0.0.0.0',
    'license': 'AGPL-3',
    'category': 'Human Resources',
    'author': "Andrei Levin, "
              "Odoo Community Association (OCA)",
    'summary': """
        Load holidays from URL that points to iCal file (*.ics)""",
    'website': "https://github.com/OCA/hr",
    # any module necessary for this one to work correctly
    'depends': [
        'hr_holidays_public'
    ],
    'data': [
        'views/hr_holidays_view.xml'
    ],
    'external_dependencies': {
        'python': [
            'vobject'
        ],
    },
    'installable': True
}
