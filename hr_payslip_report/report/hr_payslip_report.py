# -*- coding: utf-8 -*-
# © 2015 Eficent
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp.tools.sql import drop_view_if_exists


class HrPayslipReport(orm.Model):
    _name = "hr.payslip.report"
    _description = "HR Payslip Report"
    _auto = False

    _columns = {
        'struct_id': fields.many2one('hr.payroll.structure', 'Structure',
                                     required=False, readonly=True),
        'name': fields.char('Description', size=64, required=False,
                            readonly=True),
        'number': fields.char('Reference', size=64, required=False,
                              readonly=True),
        'employee_id': fields.many2one('hr.employee', 'Employee',
                                       required=False, readonly=True),
        'date_from': fields.date('Date From', readonly=True, required=False),
        'date_to': fields.date('Date To', readonly=True, required=False),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('verify', 'Waiting'),
            ('done', 'Done'),
            ('cancel', 'Rejected'),
        ], 'Status', select=True, readonly=True, required=False),
        'company_id': fields.many2one('res.company', 'Company',
                                      required=False,
                                      readonly=True),
        'paid': fields.boolean('Made Payment Order ? ',
                               required=False, readonly=True),
        'contract_id': fields.many2one('hr.contract', 'Contract',
                                       required=False, readonly=True),
        'credit_note': fields.boolean('Credit Note', readonly=True,
                                      required=False),
        'payslip_run_id': fields.many2one('hr.payslip.run',
                                          'Payslip Batches',
                                          readonly=True, required=False),
    }

    def _select(self):
        select_str = """
             SELECT min(p.id) as id,
                    p.struct_id as struct_id,
                    p.name as name,
                    p.number as number,
                    p.employee_id as employee_id,
                    p.date_from as date_from,
                    p.date_to as date_to,
                    p.state as state,
                    p.company_id as company_id,
                    p.paid as paid,
                    p.contract_id as contract_id,
                    p.credit_note as credit_note,
                    p.payslip_run_id as payslip_run_id
        """
        return select_str

    def _from(self):
        from_str = """
            FROM hr_payslip as p
        """
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY
                p.struct_id,
                p.name,
                p.number,
                p.employee_id,
                p.date_from,
                p.date_to,
                p.state,
                p.company_id,
                p.paid,
                p.contract_id,
                p.credit_note,
                p.payslip_run_id
        """
        return group_by_str

    def _where(self):
        where_str = """
        """
        return where_str

    def init(self, cr):
        drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            %s
            %s
            %s
            )""" % (self._table, self._select(), self._from(), self._where(),
                    self._group_by()))

    def unlink(self, cr, uid, ids, context=None):
        raise orm.except_orm(_('Error!'), _('You cannot delete any record!'))
