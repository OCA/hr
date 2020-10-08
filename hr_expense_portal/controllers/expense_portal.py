# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class ExpensePortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(ExpensePortal, self)._prepare_portal_layout_values()
        values['expense_count'] = request.env['hr.expense'].search_count([])
        return values

    def _expense_get_page_view_values(self, expense, access_token, **kwargs):
        values = {
            'page_name': 'expense',
            'expense': expense,
            'user': request.env.user
        }
        return self._get_page_view_values(
            expense,
            access_token,
            values,
            'my_expense_history',
            False,
            **kwargs
        )

    @http.route(
        ['/my/expenses', '/my/expenses/page/<int:page>'],
        type='http', auth="user", website=True
    )
    def portal_my_expenses(
            self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        hr_expense = request.env['hr.expense']

        domain = []

        searchbar_sortings = {
            'date': {'label': _('Date'), 'order': 'date desc'},
            'name': {'label': _('Description'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'state'},
            'sale_order_id': {'label': _('Sale Order'), 'order': 'sale_order_id'},
        }

        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        archive_groups = self._get_archive_groups('hr.expense', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin),
                       ('create_date', '<=', date_end)]

        # count for pager
        expense_count = hr_expense.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/expenses",
            url_args={'sortby': sortby},
            total=expense_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        expense = hr_expense.search(
            domain,
            order=sort_order,
            limit=self._items_per_page,
            offset=pager['offset']
        )
        request.session['my_expense_history'] = expense.ids[:100]
        values.update({
            'date': date_begin,
            'expenses': expense.sudo(),
            'page_name': 'expense',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/expenses',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("hr_expense_portal.portal_my_expenses", values)

    @http.route(
        ['/my/expense/<int:expense_id>'], type='http', auth="public", website=True
    )
    def portal_my_expense(self, expense_id, access_token=None, **kw):
        try:
            expense_sudo = self._document_check_access(
                'hr.expense', expense_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        attachment_ids = request.env['ir.attachment'].sudo().search(
            [('res_model', '=', 'hr.expense'), ('res_id', '=', expense_id)])
        values = self._expense_get_page_view_values(
            expense_sudo, access_token, **kw)
        values['attachment_ids'] = attachment_ids
        return request.render("hr_expense_portal.portal_my_expense", values)
