# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Hr Attendance Geolocation Map',
    'summary': """
        Adds a map to the attendance form view displaying the locations
        from which it was registered.
    """,
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Eficent Business and IT Consulting Services S.L.,'
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/hr',
    'depends': [
        'hr_attendance_geolocation',
        'web_widget_map',
    ],
    'data': [
        'views/assets.xml',
        'views/hr_attendance_views.xml',
    ],
    'qweb': [
        'static/src/xml/web_map.xml',
    ],
}
