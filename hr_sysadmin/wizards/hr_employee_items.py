###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import _, fields, models


class HrEmployeeItems(models.TransientModel):
    _name = 'hr.employee.items'
    _description = 'Returns the employees that has or not the selected element'

    name = fields.Char(
        string='Name',
        required=True,
    )
    product_id = fields.Many2one(
        comodel_name='product.template',
        string='Product',
        required=True,
        domain=[('internal_equipment', '=', 'True')],
    )
    does_employee_have_it = fields.Boolean(
        string='Does the employee have it?',
        default=True,
        required=True,
    )

    def employee_items_action(self):
        self.ensure_one()
        employee_ids = self.sudo().env['hr.employee'].search([
            ('item_ids.product_id', '=', self.product_id.id),
        ]).ids
        if not self.does_employee_have_it:
            not_employee_ids = self.sudo().env['hr.employee'].search([
                ('id', 'not in', employee_ids),
            ]).ids
            employee_ids = not_employee_ids
        action = {
            'type': 'ir.actions.act_window',
            'domain': [
                ('id', 'in', employee_ids),
            ],
            'view_mode': 'tree,form',
            'name': _('Employees'),
            'res_model': 'hr.employee',
        }
        return action
