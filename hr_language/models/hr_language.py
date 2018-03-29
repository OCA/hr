# -*- coding: utf-8 -*-
# © 2013 Savoir-faire Linux
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import tools
from openerp import models, fields


LANGUAGE_RATING = [
    ('0', '0 - No Proficiency'),
    ('0+', '0+ - Memorized Proficiency'),
    ('1', '1 - Elementary Proficiency'),
    ('1+', '1+ - Elementary Proficiency, Plus'),
    ('2', '2 - Limited Working Proficiency'),
    ('2+', '2+ - Limited Working Proficiency, Plus'),
    ('3', '3 - General Professional Proficiency'),
    ('3+', '3+ - General Professional Proficiency, Plus'),
    ('4', '4 - Advance Professional Proficiency'),
    ('4+', '4+ - Advance Professional Proficiency, Plus'),
    ('5', '5 - Funcionally Native Proficiency'),
]


class HrLanguage(models.Model):
    _name = 'hr.language'

    name = fields.Selection(
        tools.scan_languages(),
        string=u"Language",
        required=True,
    )

    # NOT REQUIRED SINCE 8.0.1.0.0
    description = fields.Char(
        string=u"Description",
        required=False,
    )

    employee_id = fields.Many2one(
        'hr.employee',
        string=u"Employee",
        required=True,
    )

    # DELETED SINCE 8.0.1.0.0
    # can_read = fields.Boolean(
    #     u"Read",
    #     default=True,
    #     oldname='read',
    # )
    # can_write = fields.Boolean(
    #     u"Write",
    #     default=True,
    #     oldname='write',
    # )
    # can_speak = fields.Boolean(
    #     u"Speak",
    #     default=True,
    #     oldname='speak',
    # )
    read_rating = fields.Selection(
        string='Reading',
        selection=LANGUAGE_RATING,
        required=True,
        default='0',
    )
    write_rating = fields.Selection(
        string='Writing',
        selection=LANGUAGE_RATING,
        required=True,
        default='0',
    )
    speak_rating = fields.Selection(
        string='Speaking',
        selection=LANGUAGE_RATING,
        required=True,
        default='0',
    )
    listen_rating = fields.Selection(
        string='Listening',
        selection=LANGUAGE_RATING,
        required=True,
        default='0',
    )


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    language_ids = fields.One2many(
        'hr.language',
        'employee_id',
        u"Languages",
    )
