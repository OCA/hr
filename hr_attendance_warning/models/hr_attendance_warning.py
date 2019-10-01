# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class HrAttendanceWarning(models.Model):

    _name = 'hr.attendance.warning'
    _description = 'Hr Attendance Warning'
    _inherit = 'mail.thread'
    _order = 'state, create_date desc'

    name = fields.Char(
        default='/',
        required=True,
        readonly=True
    )
    employee_id = fields.Many2one(
        'hr.employee', string='Employee', required=True,
        readonly=True, ondelete='cascade')

    department_id = fields.Many2one(
        'hr.department', related='employee_id.department_id', readonly=True,
        string="Department"
    )

    state = fields.Selection(
        [
            ('pending', 'Pending'),
            ('solved', 'Solved'),
        ], string='State',
        required=True, readonly=True,
        default='pending', track_visibility="onchange"
    )

    solved_by = fields.Many2one(
        'res.users', string='Solved by',
        readonly=True)
    solved_on = fields.Datetime(string='Solved on', readonly=True)

    solver_comment = fields.Text(
        string='Comments',
        states={'pending': [('readonly', False)]},
    )

    warning_line_ids = fields.One2many(
        'hr.attendance.warning.line',
        inverse_name='warning_id',
    )

    day_date = fields.Date(
        string='Created on',
        compute='_compute_day_date', readonly=True)

    message_preview = fields.Char(compute='_compute_message_preview',
                                  readonly=True)

    @api.depends('warning_line_ids')
    def _compute_message_preview(self):
        for warning in self:
            lines = warning.warning_line_ids.filtered(
                lambda r: r.state == 'pending'
            )
            if lines:
                warning.message_preview = lines[0].message

    @api.model
    def pending_warnings_count(self):
        warnings = {}
        for warning in self.search([('state', '=', 'pending')]):
            warnings[warning.id] = {
                'name': warning.message_preview,
                'employee': warning.employee_id.name,
                'employee_id': warning.employee_id.id,
                'icon': '/web/image?model=hr.employee&'
                        'id=%s&field=image_medium' % warning.employee_id.id,
                'date': warning.create_date,
                'count': len(warning.warning_line_ids),
                'id': warning.id
            }
        return sorted(
            list(warnings.values()), key=lambda w: w['date'], reverse=True
        )

    @api.model
    def update_counter(self):
        notifications = []
        channel = 'hr.attendance.warning'
        notifications.append([channel, {}])
        self.env['bus.bus'].sendmany(notifications)

    @api.depends('create_date')
    def _compute_day_date(self):
        for record in self:
            date_t = fields.Datetime.from_string(record.create_date)
            record.day_date = fields.Date.to_string(date_t)

    @api.model
    def get_name(self, vals):
        return self.env['ir.sequence'].next_by_code(
            'hr.attendance.warning') or '/'

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals.update({'name': self.get_name(vals)})
        res = super(HrAttendanceWarning, self).create(vals)
        self.update_counter()
        return res

    def _pending2solved_values(self):
        return {
            'state': 'solved',
            'solved_on': fields.Datetime.now(),
            'solved_by': self.env.user.id,
        }

    @api.multi
    def pending2solved(self):
        for record in self:
            record.write(record._pending2solved_values())
            for line in record.warning_line_ids:
                line.write({'state': 'solved'})
        self.update_counter()

    def _solved2pending_values(self):
        return {
            'state': 'pending',
            'solved_on': False,
            'solved_by': False,
        }

    @api.multi
    def solved2pending(self):
        for record in self:
            record.write(record._solved2pending_values())
            for line in record.warning_line_ids:
                line.write({'state': 'pending'})
        self.update_counter()

    @api.multi
    def open_employee_attendances(self):
        self.ensure_one()
        action = self.env.ref('hr_attendance.hr_attendance_action')
        result = action.read()[0]
        attendances = self.env['hr.attendance'].search(
            [('employee_id', '=', self.employee_id.id)])
        if len(attendances) > 1:
            result['domain'] = "[('id', 'in', %s)]" % attendances.ids
        elif len(attendances) == 0:
            result['domain'] = "[('id', 'in', [])]"
        else:
            result['views'] = [(False, 'form')]
            result['res_id'] = attendances.id
        result['context'] = {}
        return result


class HrAttendanceWarningLine(models.Model):

    _name = 'hr.attendance.warning.line'

    warning_id = fields.Many2one('hr.attendance.warning', readonly=True)
    employee_id = fields.Many2one('hr.employee', readonly=True,
                                  related='warning_id.employee_id')
    state = fields.Selection(
        [
            ('pending', 'Pending'),
            ('solved', 'Solved'),
        ], readonly=True,
        default='pending'
    )

    min_int = fields.Datetime(default=False, readonly=True)
    max_int = fields.Datetime(default=False, readonly=True)

    warning_type = fields.Selection(
        selection=[('no_check_in', 'Didn\'t check in'),
                   ('no_check_out', 'Didn\'t check out'),
                   ('out_of_interval', 'Out of working hours'),
                   ('no_hours', 'Not enough hours'),
                   ],
        string='Type', readonly=True,
    )

    message = fields.Char(
        string='Message',
        compute='_compute_message',
        readonly=True,
    )

    @api.depends('warning_type', 'warning_id', 'min_int', 'max_int')
    def _compute_message(self):
        for warning in self:
            if warning.warning_type == 'no_check_in':
                warning.message = _('Didn\'t check in'
                                    ' between "%s" and "%s".') % (
                    warning.min_int,
                    warning.max_int,
                )
            elif warning.warning_type == 'no_check_out':
                warning.message = _('Didn\'t check out'
                                    ' between "%s" and "%s".') % (
                    warning.min_int,
                    warning.max_int
                )
            elif warning.warning_type == 'out_of_interval':
                warning.message = _('Came to work out of working hours.')
