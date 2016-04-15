# -*- coding: utf-8 -*-
# © 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.

from dateutil.relativedelta import relativedelta

from openerp import fields, models, api
from openerp.exceptions import Warning as UserError


_tracked_states = {
    'hr_transfer.mt_alert_xfer_confirmed':
    lambda self, cr, uid, obj, ctx = None: obj['state'] == 'confirm',
    'hr_transfer.mt_alert_xfer_pending':
    lambda self, cr, uid, obj, ctx = None: obj['state'] == 'pending',
    'hr_transfer.mt_alert_xfer_done':
    lambda self, cr, uid, obj, ctx = None: obj['state'] == 'done',
}


class HrDepartmentTransfer(models.Model):
    _name = 'hr.department.transfer'
    _description = 'Departmental Transfer'
    _order = "id DESC"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    employee_id = fields.Many2one(
        'hr.employee',
        'Employee',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    src_id = fields.Many2one(
        'hr.job',
        'Job (FROM)',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    dst_id = fields.Many2one(
        'hr.job',
        'Job (TO)',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    src_department_id = fields.Many2one(
        'hr.department',
        'Department (FROM)',
        relation='src_id.department_id',
        store=True,
        readonly=True
    )
    dst_department_id = fields.Many2one(
        'hr.department',
        'Department (TO)',
        relation='dst_id.department_id',
        store=True,
        readonly=True
    )
    src_contract_id = fields.Many2one(
        'hr.contract',
        'Contract (FROM)',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    dst_contract_id = fields.Many2one(
        'hr.contract',
        'Contract (TO)',
        readonly=True
    )
    date = fields.Date(
        'Effective Date',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    note = fields.Text('Reason')
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('confirm', 'Confirmed'),
            ('pending', 'Pending'),
            ('done', 'Done'),
            ('cancel', 'Cancelled'),
        ],
        'State',
        readonly=True,
        default='draft'
    )

    _rec_name = 'date'

    _defaults = {
        'state': 'draft',
    }

    _track = {
        'state': _tracked_states,
    }

    @api.model
    def _needaction_domain_get(self):

        users_obj = self.env['res.users']
        domain = []
        if users_obj.has_group('base.group_hr_manager'):
            domain = [('state', '=', 'confirm')]
            return domain

        return False

    @api.multi
    def unlink(self, cr, uid, ids, context=None):
        transfers = self.filtered(lambda r: r.state != 'draft')
        if transfers:
            raise UserError('Unable to Delete Transfer! \n'
                            'Transfer has been initiated. Either cancel the '
                            'transfer or create another transfer to undo it')

        return super(HrDepartmentTransfer, self).unlink()

    @api.onchange('employee_id')
    @api.one
    def onchange_employee(self):
        if self.employee_id:
            employee = self.employee_id
            self.src_department_id = employee.department_id and \
                employee.department_id.id or \
                False
            self.src_id = employee.contract_id and \
                (employee.contract_id.job_id and \
                employee.contract_id_job_id.id or \
                False) or False
            self.src_contract_id = employee.contract_id and \
                self.employee_id.contract_id.id or False

    @api.model
    def _check_state(self, contract, effective_date):
        if contract.date_end and effective_date >= contract.date_end:
            raise UserError('The contract end date is on or before the '
                            'effective date of the transfer.')
        return True

    @api.multi
    def effective_date_in_future(self):
        today = fields.Date.today()
        for xfer in self:
            if xfer.date <= today:
                return False
        return True

    @api.multi
    def transfer_contract(self, contract, job_id, effective_date):
        self.ensure_one()
        # Copy the contract and adjust start/end dates,
        # job id, etc. accordingly.
        default = {
            'job_id': job_id,
            'date_start': effective_date,
            'name': '/',
            'message_ids': False,
            'trial_date_start': False,
            'trial_date_end': False,
        }
        data = contract.copy_data(default=default)
        if isinstance(data, list):
            data = data[0]

        # end the current contract
        contract.date_end = fields.Date.to_string(
            fields.Date.from_string(effective_date) + relativedelta(days=-1))

        dst_contract = self.env['hr.contract'].create(data)
        # Link to the new contract
        self.write({'dst_contract_id': dst_contract.id})

    @api.multi
    def state_confirm(self):
        for xfer in self:
            self._check_state(xfer.src_contract_id, xfer.date)
            self.write({'state': 'confirm'})
        return True

    @api.multi
    def state_done(self):

        for xfer in self:
            if xfer.date <= fields.Date.today():
                self._check_state(xfer.src_contract_id, xfer.date)
                xfer.employee_id.write(
                    {'department_id': xfer.dst_department_id.id})
                if xfer.src_contract_id:
                    xfer.transfer_contract(xfer.src_contract_id,
                                        xfer.dst_id.id, xfer.date)
                xfer.write({'state': 'done'})
            else:
                return False
        return True

    @api.model
    def try_pending_department_transfers(self):
        """Completes pending departmental transfers.
        Called from the scheduler."""
        pending_transfers = self.search(
            [
                ('state', '=', 'pending'),
                ('date', '<=', fields.Date.today()),
            ]
        )
        pending_transfers.signal_workflow('signal_done')
        return True
