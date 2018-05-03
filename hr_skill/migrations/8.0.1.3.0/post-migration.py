# -*- coding: utf-8 -*-
from openerp import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['hr.skill']._parent_store_compute()
