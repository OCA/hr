# -*- coding: utf-8 -*-

from . import models
from odoo import api, SUPERUSER_ID


def assign_old_sequences(cr, registry):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        expense_obj = env['hr.expense.sheet']
        sequence_obj = env['ir.sequence']
        for expense in expense_obj.search([], order='id'):
            expense.write({
                'number': sequence_obj.next_by_code('hr.expense.sheet')})
