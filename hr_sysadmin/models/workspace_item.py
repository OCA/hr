###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, fields, models


class WorkspaceItem(models.Model):
    _name = 'workspace.item'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Item'
    _sql_constraints = [
        (
            'sn_unique',
            'unique(sn)',
            'SN already exists!',
        ),
        (
            'internal_reference_unique_item',
            'unique(internal_reference)',
            'Internal Reference already exists!',
        ),
    ]

    name = fields.Char(
        string='Name',
        required=True,
    )
    description = fields.Text(
        string='Description',
    )
    image = fields.Binary(
        string='Image',
    )
    internal_reference = fields.Char(
        string='Internal Reference',
        copy=False,
    )
    sn = fields.Char(
        string='Serial Number',
        copy=False,
    )
    subsidy_id = fields.Many2one(
        comodel_name='workspace.item.subsidy',
        string='Subsidy',
        track_visibility='onchange',
    )
    company = fields.Selection(
        string='Company',
        selection=[
            ('modulo', 'BETA WEB DESIGN, S.L.'),
            ('kreare', 'Kreare Digital S.L.'),
            ('novotic', 'NOVOTIC, S.L.'),
            ('sdi', 'Sistemas Digitales de Informática S.L.'),
        ],
        default='sdi',
    )
    cpu = fields.Char(
        string='CPU',
    )
    ram = fields.Selection(
        selection=[
            ('RAM2GB', '2 GB'),
            ('RAM4GB', '4 GB'),
            ('RAM6GB', '6 GB'),
            ('RAM8GB', '8 GB'),
            ('RAM10GB', '10 GB'),
            ('RAM12GB', '12 GB'),
            ('RAM16GB', '16 GB'),
            ('RAM20GB', '20 GB'),
            ('RAM24GB', '24 GB'),
            ('RAM32GB', '32 GB'),
            ('RAM48GB', '48 GB'),
            ('RAM64GB', '64 GB'),
            ('RAM96GB', '96 GB'),
            ('RAM128GB', '128 GB'),
        ],
        string='RAM',
    )
    data_storage = fields.Char(
        string='Data storage',
    )
    ip = fields.Char(
        string='IP',
    )
    os_version = fields.Char(
        string='OS Version',
    )
    microsoft_office_mail = fields.Char(
        string='Microsoft Office Mail',
    )
    product_id = fields.Many2one(
        comodel_name='product.template',
        string='Product',
        required=True,
        domain=[('internal_equipment', '=', 'True')],
        track_visibility='onchange',
    )
    workspace_id = fields.Many2one(
        comodel_name='workspace.workspace',
        string='Workspace',
        group_expand='_expand_workspace_ids',
        track_visibility='onchange',
    )
    workspace_location = fields.Char(
        string='Workspace location',
        readonly=True,
        store=True,
        related='workspace_id.location',
    )
    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Employee',
        track_visibility='onchange',
    )
    employee_location = fields.Char(
        string='Employee location',
        readonly=True,
        store=True,
        related='employee_id.work_location',
    )
    is_bookable = fields.Boolean(
        string='Is bookable',
    )

    @api.model
    def _expand_workspace_ids(self, workspaces, domain, order):
        return self.env['workspace.workspace'].search([
            ('employee_ids.user_id', '=', self.env.uid)
        ])

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            if not self.name:
                self.name = self.product_id.name
            if self.product_id.image:
                self.image = self.product_id.image

    @api.onchange('workspace_id')
    def _check_workspace(self):
        if self.workspace_id:
            self.employee_id = False

    @api.onchange('employee_id')
    def _check_employee(self):
        if self.employee_id:
            self.workspace_id = False
