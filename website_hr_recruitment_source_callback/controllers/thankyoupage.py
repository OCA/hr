# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class Recruitment(http.Controller):

    @http.route(
        '/page/website_hr_recruitment.thankyou',
        type='http',
        auth="public",
        website=True
    )
    def prepare_page(self, **kw):

        context = {}
        utm_source = request.httprequest.cookies.get('odoo_utm_source')
        source = request.env['utm.source'].search([
            ('name', '=', utm_source)], limit=1)
        if source and source.js_callback_snippet:
            context = {
                'js_script' : source.js_callback_snippet,
            }
        return request.render("website_hr_recruitment.thankyou", context)
