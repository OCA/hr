# Copyright 2024 Dixmit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestTierDefinition(TransactionCase):
    def setUp(self):
        super().setUp()

        self.tier_definition = self.env["tier.definition"].create(
            {
                "name": "Test Tier Definition",
            }
        )

    def test_get_tier_validation_model_names(self):
        model_names = self.tier_definition._get_tier_validation_model_names()

        self.assertIn("hr.personal.equipment.request", model_names)
