# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "RRules in resource calendars",
    "version": "8.0.1.0.0",
    "author": "Therp BV,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Tools",
    "summary": "Use flexible repetition rules to define your employees' or "
               "machines' availability",
    "depends": [
        'resource',
        'field_rrule',
    ],
    "data": [
        "security/res_groups.xml",
        "views/templates.xml",
        "views/resource_calendar.xml",
        "views/resource_calendar_attendance.xml",
    ],
    "qweb": [
        "static/src/xml/resource_calendar_rrule.xml",
    ],
}
