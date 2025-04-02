from odoo import Command
from odoo.tests.common import (
    new_test_user,
)

from .test_governance_circle import TestGovernanceCircle


class TestPermission(TestGovernanceCircle):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.users = cls._create_test_users(
            [
                {"login": "james", "name": "James"},
                {"login": "another_kev", "name": "Kevin"},
                {"login": "bob", "name": "Bob"},
            ]
        )
        cls.james = cls.users["james"]
        cls.kevin = cls.users["another_kev"]
        cls.bob = cls.users["bob"]

        cls.memory_role = cls.env.ref(
            "hr_governance.memory_gct", raise_if_not_found=False
        )
        cls.memory_role.enable_edit_circle = True
        cls.steering_role = cls.env.ref(
            "hr_governance.steering_gct", raise_if_not_found=False
        )
        cls.facilitation_role = cls.env.ref(
            "hr_governance.facilitation_gct", raise_if_not_found=False
        )

    @classmethod
    def _create_test_users(cls, users_data):
        """Create test users and their linked employees."""
        res = {}
        for user_data in users_data:
            user = new_test_user(
                cls.env,
                login=user_data["login"],
                groups="base.group_user,hr_governance.governance_group_user",
                name=user_data["name"],
            )
            cls.env["hr.employee"].create(
                {"name": user_data["name"], "user_id": user.id}
            )
            res[user_data["login"]] = user.with_user(user)
        return res

    def _assign_role(self, circle, role, user):
        target_role = circle.child_ids.filtered_domain([("type_id", "=", role.id)])
        target_role.write(
            {"member_rel_ids": [Command.create({"member_id": user.employee_id.id})]}
        )

    def _assert_edit_access(self, circles, user, expected=True):
        accessible_ids = set(user.allowed_edit_governance_ids.ids)
        if len(circles) == 1:
            circle_id = circles.id
            if expected:
                self.assertIn(circle_id, accessible_ids)
            else:
                self.assertNotIn(circle_id, accessible_ids)
        else:
            circle_ids = [circle.id for circle in circles]
            if expected:
                self.assertTrue(set(circle_ids).issubset(accessible_ids))
            else:
                self.assertFalse(any(id in accessible_ids for id in circle_ids))

    def _assert_children_edit_access(self, circle, user, all_expected=True):
        child_ids = circle.child_ids.ids
        accessible_ids = set(user.allowed_edit_governance_ids.ids)
        if all_expected:
            self.assertTrue(set(child_ids).issubset(accessible_ids))
        else:
            self.assertFalse(set(child_ids).issubset(accessible_ids))

    def test_01(self):
        """The "Memory"/Steering Role is Assigned Within the Circle"""
        test_circle = (
            self.env["governance.circle"]
            .with_context(default_is_circle=True)
            .create(
                {
                    "name": "Test Circle",
                    "parent_id": self.env.ref("hr_governance.root").id,
                }
            )
        )
        self._assign_role(test_circle, self.memory_role, self.james)
        self._assign_role(test_circle, self.facilitation_role, self.bob)

        self.env.invalidate_all()
        self._assert_edit_access(test_circle, self.james)
        self._assert_children_edit_access(test_circle, self.james)

        self._assert_edit_access(test_circle, self.bob, False)
        self._assert_children_edit_access(test_circle, self.bob, False)

        # Steering is assigned
        self._assign_role(test_circle, self.steering_role, self.kevin)
        self.env.invalidate_all()

        # as Memory is still assigned, steering is not allowed
        self._assert_edit_access(test_circle, self.kevin, False)
        self._assert_children_edit_access(test_circle, self.kevin, False)

        # Un-assign Memory
        test_circle.child_ids.filtered_domain(
            [("type_id", "=", self.memory_role.id)]
        ).member_rel_ids.unlink()
        self.env.invalidate_all()

        # as Memory is un-assigned, steering is allowed_edit_governance_ids
        self._assert_edit_access(test_circle, self.kevin)
        self._assert_children_edit_access(test_circle, self.kevin)

        self._assert_edit_access(test_circle, self.james, False)
        self.assertFalse(self.james.allowed_edit_governance_ids)

    def test_02(self):
        """Neither "Memory" nor "Steering" Roles Are Assigned in the Circle,
        but the Parent Circle Has a "Memory"/Steering Role"""
        circle = (
            self.env["governance.circle"]
            .with_context(default_is_circle=True)
            .create(
                {
                    "name": "Circle",
                    "parent_id": self.env.ref("hr_governance.root").id,
                }
            )
        )
        self._assign_role(circle, self.memory_role, self.james)
        subcircle = (
            self.env["governance.circle"]
            .with_context(default_is_circle=True)
            .create(
                {
                    "name": "SubCircle",
                    "parent_id": circle.id,
                }
            )
        )
        self._assign_role(subcircle, self.facilitation_role, self.bob)
        self.env.invalidate_all()

        self._assert_edit_access(circle | subcircle, self.james)
        self._assert_children_edit_access(circle, self.james)

        self._assert_edit_access(circle | subcircle, self.bob, False)
        self._assert_children_edit_access(subcircle, self.bob, False)

        # circle has both Memory and Steering assigned,
        # only Memory is allowed to update subcircle
        self._assign_role(circle, self.steering_role, self.kevin)
        self.env.invalidate_all()
        self._assert_edit_access(circle | subcircle, self.james)
        self._assert_children_edit_access(circle, self.james)

        self._assert_edit_access(circle | subcircle, self.kevin, False)

    def test_03(self):
        """Neither "Memory" nor "Steering" Roles Are Assigned in the Circle
        or in the Parent Circle"""
        circle = (
            self.env["governance.circle"]
            .with_context(default_is_circle=True)
            .create(
                {
                    "name": "Circle",
                    "parent_id": self.env.ref("hr_governance.root").id,
                }
            )
        )
        self._assign_role(circle, self.facilitation_role, self.james)

        subcircle = (
            self.env["governance.circle"]
            .with_context(default_is_circle=True)
            .create(
                {
                    "name": "SubCircle",
                    "parent_id": circle.id,
                }
            )
        )
        self._assign_role(subcircle, self.facilitation_role, self.bob)
        self.env.invalidate_all()

        self._assert_edit_access(circle | subcircle, self.james, False)
        self._assert_children_edit_access(circle, self.james, False)

        self._assert_edit_access(circle | subcircle, self.bob, False)
        self._assert_children_edit_access(subcircle, self.bob, False)

    def test_04(self):
        """Complex Inheritance Chain Across Multiple Levels"""
        circle_level_1 = (
            self.env["governance.circle"]
            .with_context(default_is_circle=True)
            .create(
                {
                    "name": "Circle level 1",
                    "parent_id": self.env.ref("hr_governance.root").id,
                }
            )
        )
        self._assign_role(circle_level_1, self.memory_role, self.james)

        circle_level_2 = (
            self.env["governance.circle"]
            .with_context(default_is_circle=True)
            .create(
                {
                    "name": "Circle level 2",
                    "parent_id": circle_level_1.id,
                }
            )
        )
        self._assign_role(circle_level_2, self.steering_role, self.kevin)

        circle_level_3 = (
            self.env["governance.circle"]
            .with_context(default_is_circle=True)
            .create(
                {
                    "name": "Circle level 3",
                    "parent_id": circle_level_2.id,
                }
            )
        )
        self._assign_role(circle_level_3, self.facilitation_role, self.bob)
        self.env.invalidate_all()

        # For Circle level 1
        self._assert_edit_access(circle_level_1, self.james)
        self.assertNotIn(
            circle_level_1.id,
            self.kevin.allowed_edit_governance_ids.ids
            + self.bob.allowed_edit_governance_ids.ids,
        )

        # For Circle level 2
        self._assert_edit_access(circle_level_2, self.kevin)

        # as circle_level_2 is assigned, james cannot touch it and its subcircles
        self._assert_edit_access(circle_level_2, self.james, False)
        self.assertNotIn(
            circle_level_2.child_ids.ids, self.james.allowed_edit_governance_ids.ids
        )

        # For Circle level 3
        self._assert_edit_access(circle_level_3, self.kevin)
        self._assert_edit_access(
            circle_level_3 | circle_level_3.child_ids, self.james, False
        )
        self._assert_edit_access(circle_level_3, self.bob, False)
        self._assert_children_edit_access(circle_level_3, self.bob, False)
