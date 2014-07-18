# -*- coding: utf-8 -*-
#
#
#    Daniel Reis, 2011
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

from osv import osv


def ext_name_get(self, cr, uid, ids, name_templ, flds_templ, context=None):
    """
     Usage:
    import reis_base as util
    (...)
        def name_get(self, cr, uid, ids, context=None):
            return util.ext_name_get(self, cr, uid, ids, '[%(ref)s] %(name)s', ['ref', 'name'], context=context)
    <= edit name template mask
    """
    name_templ = name_templ or '%(' + self._rec_name + ')s'
    # template and columns list must be provided
    if ids and name_templ:
        # Get fields list, if not provided (warning: slower!)
        # Exclude function fields to avoid recursion
        # if not flds_templ:
        #    flds_all = self.fields_get(cr, uid)
        #    flds_templ = [ x for x in flds_all if x!='id' and not flds_all[x].get('function')]
        res = []
        for rec in self.read(cr, uid, ids, ['id'] + flds_templ, context=context):
            # Prepare values
            for key in rec:
                # Set default for empty values
                if not rec[key]:
                    rec[key] = ''
                # Extract names from tuples (id, name) in many2one fields
                if type(rec[key]) == tuple:
                    rec[key] = rec[key][1]
            try:
                n = name_templ % rec
            except:
                n = '<name_get failed!>'
            res.append((rec['id'], n))
            # rint '...name_get', name_templ, rec
    else:
        # if not, use the deafult name_get()
        res = super(osv.osv, self).name_get(cr, uid, ids, context=context)
    return res


def ext_name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100, keys=None):
    """
    Usage:
    import reis_base as util
    (...)
        def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
                return util.ext_name_search(self, cr, user, name, args, operator, context=context, limit=limit,
     keys=['ref','name']) #<=edit list of fields to search
    """
    if not args:
        args = []
    if not keys:
        keys = [name]
    # rint 'name_search', keys, args, operator, name.encode('utf-8')
    if name:
        for key in keys:
            ids = self.search(
                cr, user, [(key, operator, name)] + args, limit=limit, context=context)
            # Exit loop on first results
            if len(ids):
                break
        # rint '...key ', key, ids
    else:
        ids = self.search(cr, user, args, limit=limit, context=context)
        # rint '...nokey:', ids
    result = self.name_get(cr, user, ids, context=context)
    return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
