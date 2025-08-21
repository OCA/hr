from odoo import Command
from odoo.tests.common import (
    new_test_user,
)

from .test_governance_circle import TestGovernanceCircle


class TestPermission(TestGovernanceCircle):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.james = cls._create_test_user(login="james", name="James")
        cls.kevin = cls._create_test_user(login="another_kev", name="Kevin")
        cls.bob = cls._create_test_user(login="bob", name="Bob")

        cls.memory_role = cls.env.ref("hr_governance.memory_gct")
        cls.memory_role.enable_edit_circle = True
        cls.steering_role = cls.env.ref("hr_governance.steering_gct")
        cls.facilitation_role = cls.env.ref("hr_governance.facilitation_gct")

    @classmethod
    def _create_test_user(cls, login, name):
        user = new_test_user(
            cls.env,
            login=login,
            groups="base.group_user,hr_governance.governance_group_user",
            name=name,
        )
        cls.env["hr.employee"].create({"name": name, "user_id": user.id})
        return user.with_user(user)

    def _create_circle(self, name, parent):
        return (
            self.env["governance.circle"]
            .with_context(default_is_circle=True)
            .create(
                {
                    "name": name,
                    "parent_id": parent.id,
                }
            )
        )

    def _assign_role(self, circle, role, user):
        """Assigns a role to a user within a specific circle."""
        target_role = circle.child_ids.filtered(lambda r: r.type_id == role)
        target_role.role_assignment_ids = [
            Command.create({"member_id": user.employee_id.id})
        ]

    def _unassign_role(self, circle, role):
        """Unassigns a role from a circle."""
        target_role = circle.child_ids.filtered(lambda r: r.type_id == role)
        target_role.role_assignment_ids.unlink()

    def _assert_user_can_edit_circles(self, user, circles):
        """Asserts that the user has edit access to all given circles."""
        accessible_ids = user.allowed_edit_governance_ids.ids
        self.assertTrue(set(circles.ids).issubset(accessible_ids))

    def _assert_user_cannot_edit_circles(self, user, circles):
        """Asserts that the user has no edit access to any of the given circles."""
        accessible_ids = user.allowed_edit_governance_ids.ids
        self.assertFalse(any(cid in accessible_ids for cid in circles.ids))

    def _get_subcircles(self, circle):
        """Returns the subcircles of a given circle."""
        return circle.child_ids.filtered("is_circle")

    def _assert_user_can_edit_all_subcircles(self, user, circle):
        """Asserts that the user has edit access to all subcircles of a given circle."""
        subcircles = self._get_subcircles(circle)
        if subcircles:
            self._assert_user_can_edit_circles(user, subcircles)

    def _assert_user_cannot_edit_any_subcircles(self, user, circle):
        """Asserts that the user has no edit access to any of the subcircles."""
        subcircles = self._get_subcircles(circle)
        if subcircles:
            self._assert_user_cannot_edit_circles(user, subcircles)

    def test_permission_granted_when_memory_or_steering_role_is_in_circle(self):
        """
        Test case where the "Memory" or "Steering" role is assigned within the circle.
        - A user with the "Memory" role should have edit access.
        - A user with another role (e.g., "Facilitation") should not.
        - If "Memory" is present, "Steering" role does not grant access.
        - If "Memory" is unassigned, "Steering" role grants access.
        """
        # Arrange: Create a test circle and assign roles
        root_circle = self.env.ref("hr_governance.root")
        test_circle = self._create_circle("Test Circle", root_circle)
        self._assign_role(test_circle, self.memory_role, self.james)
        self._assign_role(test_circle, self.facilitation_role, self.bob)
        self.env.invalidate_all()

        # Act & Assert: James (Memory) has access, Bob (Facilitation) does not
        self._assert_user_can_edit_circles(self.james, test_circle)
        self._assert_user_can_edit_all_subcircles(self.james, test_circle)
        self._assert_user_cannot_edit_circles(self.bob, test_circle)
        self._assert_user_cannot_edit_any_subcircles(self.bob, test_circle)

        # Act: Assign Steering role to Kevin
        self._assign_role(test_circle, self.steering_role, self.kevin)
        self.env.invalidate_all()

        # Assert: Kevin (Steering) has no access because Memory role is still assigned
        self._assert_user_cannot_edit_circles(self.kevin, test_circle)
        self._assert_user_cannot_edit_any_subcircles(self.kevin, test_circle)

        # Act: Un-assign Memory role
        self._unassign_role(test_circle, self.memory_role)
        self.env.invalidate_all()

        # Assert: Kevin (Steering) now has access
        self._assert_user_can_edit_circles(self.kevin, test_circle)
        self._assert_user_can_edit_all_subcircles(self.kevin, test_circle)

        # Assert: James (former Memory) has no access anymore
        self._assert_user_cannot_edit_circles(self.james, test_circle)
        self.assertFalse(self.james.allowed_edit_governance_ids)

    def test_permission_inherited_from_parent_circle(self):
        """
        Test case where permissions are inherited from a parent circle that has a
        "Memory" or "Steering" role.
        """
        # Arrange: Create parent and sub-circle, assign roles
        root_circle = self.env.ref("hr_governance.root")
        parent_circle = self._create_circle("Parent Circle", root_circle)
        self._assign_role(parent_circle, self.memory_role, self.james)
        subcircle = self._create_circle("SubCircle", parent_circle)
        self._assign_role(subcircle, self.facilitation_role, self.bob)
        self.env.invalidate_all()

        # Act & Assert: James (Memory in parent) has access to both circles
        self._assert_user_can_edit_circles(self.james, parent_circle | subcircle)
        self._assert_user_can_edit_all_subcircles(self.james, parent_circle)

        # Act & Assert: Bob (Facilitation in subcircle) has no access to either
        self._assert_user_cannot_edit_circles(self.bob, parent_circle | subcircle)
        self._assert_user_cannot_edit_any_subcircles(self.bob, subcircle)

        # Act: Assign Steering role in parent circle to Kevin
        self._assign_role(parent_circle, self.steering_role, self.kevin)
        self.env.invalidate_all()

        # Assert: James still has access, Kevin does not (Memory takes precedence)
        self._assert_user_can_edit_circles(self.james, parent_circle | subcircle)
        self._assert_user_can_edit_all_subcircles(self.james, parent_circle)
        self._assert_user_cannot_edit_circles(self.kevin, parent_circle | subcircle)

    def test_no_permission_if_no_granting_role_in_hierarchy(self):
        """
        Test case where neither the circle nor its parent have a "Memory" or
        "Steering" role.
        """
        # Arrange: Create circles with only a non-permission-granting role
        root_circle = self.env.ref("hr_governance.root")
        circle = self._create_circle("Circle", root_circle)
        self._assign_role(circle, self.facilitation_role, self.james)
        subcircle = self._create_circle("SubCircle", circle)
        self._assign_role(subcircle, self.facilitation_role, self.bob)
        self.env.invalidate_all()

        # Act & Assert: No user has edit access
        self._assert_user_cannot_edit_circles(self.james, circle | subcircle)
        self._assert_user_cannot_edit_any_subcircles(self.james, circle)
        self._assert_user_cannot_edit_circles(self.bob, circle | subcircle)
        self._assert_user_cannot_edit_any_subcircles(self.bob, subcircle)

    def test_permission_inheritance_in_deeply_nested_circles(self):
        """Test complex permission inheritance across multiple levels of circles."""
        # Arrange: Create a 3-level hierarchy of circles with different roles
        root_circle = self.env.ref("hr_governance.root")
        circle_l1 = self._create_circle("Circle L1", root_circle)
        self._assign_role(circle_l1, self.memory_role, self.james)

        circle_l2 = self._create_circle("Circle L2", circle_l1)
        self._assign_role(circle_l2, self.steering_role, self.kevin)

        circle_l3 = self._create_circle("Circle L3", circle_l2)
        self._assign_role(circle_l3, self.facilitation_role, self.bob)
        self.env.invalidate_all()

        # Act & Assert: Check permissions at each level
        # Level 1: Only James (Memory in L1) has access to L1
        self._assert_user_can_edit_circles(self.james, circle_l1)
        self._assert_user_cannot_edit_circles(self.kevin, circle_l1)
        self._assert_user_cannot_edit_circles(self.bob, circle_l1)

        # Level 2: Kevin (Steering in L2) has access, overriding James from L1
        self._assert_user_can_edit_circles(self.kevin, circle_l2)
        self._assert_user_cannot_edit_circles(self.james, circle_l2)
        self._assert_user_cannot_edit_circles(self.bob, circle_l2)

        # Level 3: Kevin's permission from L2 is inherited by L3
        self._assert_user_can_edit_circles(self.kevin, circle_l3)
        self._assert_user_cannot_edit_circles(self.james, circle_l3)
        self._assert_user_cannot_edit_circles(self.bob, circle_l3)
        self._assert_user_cannot_edit_any_subcircles(self.bob, circle_l3)
