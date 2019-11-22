# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Hr Attendance Permitted Geolocation',
    'summary': """
        With this module the user can set a maximum range within which
        the check-in/check-out process must be done. Registering attendance
        outside this range will trigger an error.
    """,
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Eficent Business and IT Consulting Services S.L.,'
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/hr',
    'depends': [
        'hr_attendance_geolocation',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_attendance_location_views.xml',
        'views/res_config_settings_views.xml',
    ],
}
