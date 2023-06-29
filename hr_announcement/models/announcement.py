# Copyright 2023 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class Announcement(models.Model):
    _inherit = "announcement"

    announcement_type = fields.Selection(
        selection_add=[
            ("employee", "Employee"),
            ("department", "Department"),
            ("job_position", "Job Position"),
        ],
        ondelete={
            "employee": "set default",
            "department": "set default",
            "job_position": "set default",
        },
    )
    employee_ids = fields.Many2many(
        comodel_name="hr.employee",
        string="Employees",
    )
    department_ids = fields.Many2many(
        comodel_name="hr.department",
        string="Departments",
    )
    position_ids = fields.Many2many(
        comodel_name="hr.job",
        string="Job Positions",
    )

    def _update_read_unread_announcements(self):
        """Used to set users unread announcements when they're set in the announcement
        itself"""
        for announcement in self:
            for employee in announcement.employee_ids.filtered(
                lambda x: x.user_id
                and announcement
                not in (
                    x.user_id.read_announcement_ids + x.user_id.unread_announcement_ids
                )
            ):
                employee.user_id.unread_announcement_ids |= announcement

    @api.model
    def create(self, vals):
        announcement = super().create(vals)
        if vals.get("employee_ids"):
            announcement._update_read_unread_announcements()
        return announcement

    def write(self, vals):
        res = super().write(vals)
        if vals.get("employee_ids"):
            self._update_read_unread_announcements()
        return res

    @api.depends(
        "specific_user_ids",
        "user_group_ids",
        "employee_ids",
        "department_ids",
        "position_ids",
    )
    def _compute_allowed_user_ids(self):
        excluded_announcement_types = self.filtered(
            lambda a: a.announcement_type in ["employee", "department", "job_position"]
        )
        res = super(
            Announcement, self - excluded_announcement_types
        )._compute_allowed_user_ids()
        for announcement in self.filtered(lambda a: a.announcement_type == "employee"):
            announcement.allowed_user_ids = announcement.employee_ids.user_id
            announcement.allowed_users_count = len(announcement.employee_ids.user_id)
        for announcement in self.filtered(
            lambda a: a.announcement_type == "department"
        ):
            announcement.allowed_user_ids = (
                announcement.department_ids.member_ids.user_id
            )
            announcement.allowed_users_count = len(
                announcement.department_ids.member_ids.user_id
            )
        for announcement in self.filtered(
            lambda a: a.announcement_type == "job_position"
        ):
            announcement.allowed_user_ids = announcement.position_ids.mapped(
                "employee_ids.user_id"
            )
            announcement.allowed_users_count = len(
                announcement.position_ids.mapped("employee_ids.user_id")
            )
        return res

    @api.onchange("announcement_type")
    def _onchange_announcement_type(self):
        res = super()._onchange_announcement_type()
        if self.announcement_type == "specific_users":
            self.employee_ids = False
            self.department_ids = False
            self.position_ids = False
        elif self.announcement_type == "user_group":
            self.employee_ids = False
            self.department_ids = False
            self.position_ids = False
        elif self.announcement_type == "employee":
            self.user_group_ids = False
            self.specific_user_ids = False
            self.department_ids = False
            self.position_ids = False
        elif self.announcement_type == "department":
            self.user_group_ids = False
            self.specific_user_ids = False
            self.employee_ids = False
            self.position_ids = False
        elif self.announcement_type == "job_position":
            self.user_group_ids = False
            self.specific_user_ids = False
            self.employee_ids = False
            self.department_ids = False
        return res
