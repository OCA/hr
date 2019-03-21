# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrWorkAccident(models.Model):

    _name = 'hr.work.accident'
    _description = 'Hr Work Accident'

    name = fields.Char(readonly=True, required=True, default="/")
    company_id = fields.Many2one('res.company', string='Company')
    department_id = fields.Many2one('hr.department', string='Department')
    job_position = fields.Many2one('hr.job', string='Job Position')
    # job center
    day_of_week = fields.Char(string='Day of week',
                              compute='_compute_day_of_week')
    date = fields.Datetime(string='Accident Date', required=True)
    date_end = fields.Datetime(string='Investigation End Date', readonly=True)
    hours_working = fields.Float(
        string='Working Hour',
        help='Amount of hours the employee had '
             'been working when the accident happened',
        required=True,
    )
    location = fields.Char(string="Accident Location", required=True)
    description = fields.Text(string="Description", required=True)
    causes = fields.Text(string="Causes", required=True)
    affected_employees = fields.One2many(
        'hr.work.accident.employee',
        string="Affected employees",
        inverse_name='accident_id',
    )

    accident_type = fields.Many2one('hr.work.accident.type', required=True)

    risks = fields.One2many(
        'hr.work.accident.risk',
        string="Detected Risks",
        inverse_name='accident_id',
    )

    actions = fields.One2many(
        'hr.work.accident.action',
        string="Detected Risks",
        inverse_name='accident_id',
    )

    state = fields.Selection(
        [('open', 'Open'), ('closed', 'Closed')],
        default='open',
        readonly=True,
    )

    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        default=lambda self: self.env.user.company_id.currency_id,
    )
    total_cost = fields.Monetary(
        string='Corrective actions cost',
        compute='_compute_cost_sum',
    )

    @api.multi
    def finish_investigation(self):
        for record in self:
            record.state = 'closed'
            record.date_end = fields.Datetime.now()

    @api.multi
    def back_to_open(self):
        for record in self:
            record.state = 'open'

    @api.depends('actions')
    def _compute_cost_sum(self):
        for record in self:
            record.total_cost = sum([action.cost for action in record.actions])

    @api.depends('date')
    def _compute_day_of_week(self):
        week = ['Monday',
                'Tuesday',
                'Wednesday',
                'Thursday',
                'Friday',
                'Saturday',
                'Sunday']
        for record in self:
            date = fields.Datetime.from_string(record.date)
            record.day_of_week = week[date.weekday()]

    @api.model
    def get_name(self, vals):
        return self.env['ir.sequence'].next_by_code(
            'hr.work.accident') or '/'

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals.update({'name': self.get_name(vals)})
        return super(HrWorkAccident, self).create(vals)


class HrWorkAccidentEmployee(models.Model):

    _name = 'hr.work.accident.employee'

    employee_id = fields.Many2one('hr.employee', string="Employee")
    injury_severity = fields.Selection(
        selection=[
            ('slight', 'Slight wound'),
            ('serious', 'Serious'),
            ('very_serious', 'Very serious'),
            ('death', 'Death'),
        ],
        string='Severity'
    )
    accident_id = fields.Many2one('hr.work.accident', string="Accident")
    injury_type = fields.Char(string="Injury type")
    seniority = fields.Float(
        related='employee_id.length_of_service',
        readonly=True,
        string='Seniority in the company (in months)',
    )
    seniority_position = fields.Float(
        string='Seniority in the position (in months)',
    )


class HrWorkAccidentRisk(models.Model):

    _name = 'hr.work.accident.risk'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string="Description", required=True)
    accident_id = fields.Many2one('hr.work.accident', string="Accident")
    consequences = fields.Selection(
        selection=[
            ('catastrophic', 'Catastrophic'),
            ('disaster', 'Disaster'),
            ('very_serious', 'Very Serious'),
            ('serious', 'Serious'),
            ('important', 'Important'),
            ('slight', 'Slight'),
        ], required=True
    )
    probability = fields.Selection(
        selection=[
            ('very_likely', 'Very likely'),
            ('likely', 'Likely'),
            ('possible', 'Possible'),
            ('rare', 'Rare'),
            ('very_rare', 'Very rare'),
            ('almost_impossible', 'Almost Impossible'),
        ], required=True
    )
    magnitude = fields.Selection(
        selection=[
            ('very_high', 'Very high'),
            ('high', 'High'),
            ('normal', 'Normal'),
            ('low', 'Low'),
            ('very_low', 'Very low'),
        ], required=True
    )
    frequency = fields.Selection(
        selection=[
            ('continuous', 'Continuous'),
            ('frequent', 'Frequent'),
            ('Ocasional', 'Ocasional'),
            ('Unusual', 'Unusual'),
            ('Inexistent', 'Inexistent'),
        ], required=True
    )


class HrWorkAccidentAction(models.Model):

    _name = 'hr.work.accident.action'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string="Description", required=True)
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        default=lambda self: self.env.user.company_id.currency_id,
    )
    cost = fields.Monetary(string='Cost', required=True,)
    action_date = fields.Date(string="Planned Date")
    employee_ids = fields.Many2many('hr.employee',
                                    string='Employees in charge')
    accident_id = fields.Many2one('hr.work.accident', string="Accident")


class HrWorkAccidentType(models.Model):

    _name = 'hr.work.accident.type'

    name = fields.Char(string='Name', required=True)
