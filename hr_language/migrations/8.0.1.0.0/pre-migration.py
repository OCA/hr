# -*- coding: utf-8 -*-
# © 2013 Savoir-faire Linux
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def migrate(cr, version):
    if not version:
        return
#
#     cr.execute(
#         'ALTER TABLE hr_language '
#         'RENAME TO migration_hr_language')
