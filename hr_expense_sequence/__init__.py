# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from . import models
from openerp import SUPERUSER_ID


def assign_old_sequences(cr, registry):
    expense_obj = registry['hr.expense.expense']
    sequence_obj = registry['ir.sequence']
    expense_ids = expense_obj.search(cr, SUPERUSER_ID, [], order="id")
    for expense_id in expense_ids:
        expense_obj.write(cr, SUPERUSER_ID, expense_id,
                          {'number': sequence_obj.get(
                              cr, SUPERUSER_ID, 'hr.expense')})
