# Copyright (C) 2020 - TODAY, Marcel Savegnago - Escodoo).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.tools.translate import _
from odoo.addons.portal.controllers.portal import pager as portal_pager, CustomerPortal
from odoo.osv.expression import OR


class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        values['hr_applicant_count'] = request.env[
            'hr.applicant'].search_count([])
        return values

    def _hr_applicant_get_page_view_values(self, hr_applicant,
                                           access_token, **kwargs):
        values = {
            'page_name': 'hr_applicant',
            'hr_applicant': hr_applicant,
        }
        return self._get_page_view_values(
            hr_applicant, access_token, values,
            'my_hr_applicants_history', False, **kwargs)

    @http.route(
        ['/my/hr_applicants', '/my/hr_applicants/page/<int:page>'],
        type='http', auth="user", website=True)
    def portal_my_HR_hr_applicants(self, page=1, date_begin=None,
                                   date_end=None, sortby=None,
                                   search=None, search_in='name', **kw):
        values = self._prepare_portal_layout_values()
        domain = []

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }
        searchbar_inputs = {
            'content': {'input': 'content', 'label': _(
                'Search <span class="nolabel"> (in Content)</span>')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }

        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # archive groups - Default Group By 'create_date'
        archive_groups = self._get_archive_groups('hr.applicant', domain)
        if date_begin and date_end:
            domain += [
                ('create_date', '>', date_begin),
                ('create_date', '<=', date_end),
            ]

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('content', 'all'):
                search_domain = OR([search_domain, [
                    '|', ('name', 'ilike', search), ('content', 'ilike', search)]])
            domain += search_domain

        # pager
        hr_applicants_count = request.env['hr.applicant'].search_count(domain)
        pager = portal_pager(
            url="/my/hr_applicants",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=hr_applicants_count,
            page=page,
            step=self._items_per_page
        )

        hr_applicants = request.env['hr.applicant'].search(
            domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_hr_applicants_history'] = hr_applicants.ids[:100]

        values.update({
            'date': date_begin,
            'hr_applicants': hr_applicants,
            'page_name': 'hr_applicant',
            'default_url': '/my/hr_applicants',
            'pager': pager,
            'archive_groups': archive_groups,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'sortby': sortby,
            'search_in': search_in,
            'search': search,
        })
        return request.render(
            "hr_recruitment_portal.portal_my_HR_hr_applicants", values)

    @http.route([
        "/recruitment/hr_applicant/<int:hr_applicant_id>",
        "/recruitment/hr_applicant/<int:hr_applicant_id>/<token>",
        '/my/hr_applicant/<int:hr_applicant_id>'
    ], type='http', auth="public", website=True)
    def hr_applicants_followup(self, hr_applicant_id=None,
                               access_token=None, **kw):
        try:
            hr_applicant_sudo = self._document_check_access(
                'hr.applicant', hr_applicant_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = self._hr_applicant_get_page_view_values(
            hr_applicant_sudo, access_token, **kw)
        return request.render(
            "hr_recruitment_portal.hr_applicants_followup", values)
