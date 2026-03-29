from odoo import fields, models


class WellnessQuestion(models.Model):
    """
    Surfacing Questions for Daily Wellness Checks.

    This model allows HR admins to define which questions are presented
    to employees during the daily login prompt. The system currently
    supports displaying up to three active questions in the wizard.
    """

    _name = "wellness.question"
    _description = "Wellness Question"
    _order = "sequence, id"

    name = fields.Char(
        string="Question",
        required=True,
        help="The text of the question to ask employees.",
    )
    active = fields.Boolean(
        default=True,
        help="Only active questions will be included in the daily survey.",
    )
    sequence = fields.Integer(
        default=10,
        help="Determines the order of questions in the UI.",
    )
