from odoo.tests.common import (
    TransactionCase,
)
from odoo.tools import convert_file

DATA_FILES = ["tests/governance_circle_data.xml"]


class TestGovernanceCircle(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.load_data()

    @classmethod
    def load_data(cls):
        for filename in DATA_FILES:
            convert_file(
                cls.env,
                module="hr_governance",
                filename=filename,
                idref={},
                mode="init",
                noupdate=False,
                kind="test",
            )

    def test_circle_automation(self):
        """
        When creating a circle, there should be structuring roles created automatically
        and assigned to the circle
        """
        circle_1 = (
            self.env["governance.circle"]
            .with_context(default_is_circle=True)
            .create(
                {
                    "name": "Test Circle 1",
                    "parent_id": self.env.ref(
                        "hr_governance.root", raise_if_not_found=False
                    ).id,
                }
            )
        )
        structuring_roles = circle_1.child_ids.filtered(
            lambda x: x.type_id.type == "structure"
        )
        self.assertTrue(
            all(role.purpose == role.type_id.purpose for role in structuring_roles)
        )
        self.assertTrue(
            all(role.authority == role.type_id.authority for role in structuring_roles)
        )
        self.assertTrue(
            all(
                role.expectation == role.type_id.expectation
                for role in structuring_roles
            )
        )
