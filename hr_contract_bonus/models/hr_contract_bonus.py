# Copyright 2025 APSL-Nagarro Antoni Marroig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Bonus(models.Model):
    _name = "hr.contract.bonus"
    _description = "Employee Contract Bonus"

    name = fields.Char(
        required=True,
        help="Name of the bonus to be applied to the employee's contract.",
    )
    amount = fields.Float(
        string="Bonus Amount",
        help="The amount of the bonus to be applied to the employee's contract.",
        required=True,
    )
    type = fields.Selection(
        selection=[
            ("fixed", "Fixed Amount"),
            ("percentage", "Percentage of Salary"),
        ],
        string="Bonus Type",
        default="fixed",
        help="Type of bonus to be applied. Fixed amount or percentage of the salary.",
        required=True,
    )
    frequency = fields.Selection(
        selection=[
            ("monthly", "Monthly"),
            ("yearly", "Yearly"),
        ],
        string="Bonus Frequency",
        default="monthly",
        help="Frequency at which the bonus is applied to the employee's contract.",
        required=True,
    )
