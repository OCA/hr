# -*- coding: utf-8 -*-
# © 2011 Michael Telahun Makonnen <mmakonnen@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import fields, orm


class hr_employee(orm.Model):

    _name = 'hr.employee'
    _inherit = 'hr.employee'

    _columns = {
        'ec_name': fields.char(
            'Name',
            size=256,
        ),
        'ec_relationship': fields.char(
            'Relationship',
            size=64,
        ),
        'ec_tel1': fields.char(
            'Primary Phone No.',
            size=32,
        ),
        'ec_tel2': fields.char(
            'Secondary Phone No.',
            size=32,
        ),
        'ec_woreda': fields.char(
            'Subcity/Woreda',
            size=32,
        ),
        'ec_kebele': fields.char(
            'Kebele',
            size=8,
        ),
        'ec_houseno': fields.char(
            'House No.',
            size=8,
        ),
        'ec_address': fields.char(
            'Address 2',
            size=256,
        ),
        'ec_country_id': fields.many2one(
            'res.country',
            'Country',
        ),
        'ec_state_id': fields.many2one(
            'res.country.state',
            'State',
            domain="[('country_id','=',country_id)]",
        ),
    }

    def _get_country(self, cr, uid, context=None):
        cid = self.pool.get('res.country').search(
            cr, uid, [('code', '=', 'ET')], context=context
        )
        return cid[0]

    _defaults = {
        'ec_country_id': _get_country,
    }
