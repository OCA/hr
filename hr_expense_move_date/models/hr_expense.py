# -*- coding: utf-8 -*-
# Copyright 2016-17 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    move_date = fields.Date(
        string='Move Date',
        related="sheet_id.accounting_date",
        readonly=True,
        oldname='move_date'
    )
