# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Hr Attendance Geolocation',
    'summary': """
        With this module the geolocation of the user is tracked at the
        check-in/check-out step""",
    'version': '12.0.1.0.1',
    'license': 'AGPL-3',
    'author': 'Eficent Business and IT Consulting Services S.L.,'
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/hr',
    'depends': [
        'decimal_precision',
        'hr_attendance',
    ],
    'data': [
        'views/assets.xml',
        'views/hr_attendance_views.xml',
        'data/location_data.xml',
    ],
}
