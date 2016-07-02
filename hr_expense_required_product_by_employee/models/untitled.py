# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models, _
from openerp.exceptions import except_orm
from lxml import etree
from openerp.osv.orm import transfer_modifiers_to_node


class HrExpense(models.Model):	
    _inherit = 'hr.expense.expense'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super(HrExpense, self).fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu)
        if view_type != 'form':
            return res
        if 'line_ids' not in res['fields']:
            return res
        line_field = res['fields']['line_ids']
        for view_type, view in line_field['views'].iteritems():
            if view_type not in ('tree', 'form'):
                continue
            field = view['fields']['product_id']
            modifiers = {'required': True}
            transfer_modifiers_to_node(modifiers, field[0])
        return res
