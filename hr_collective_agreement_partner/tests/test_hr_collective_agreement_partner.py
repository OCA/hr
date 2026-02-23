# Copyright 2025 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestCollectiveAgreement(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env["res.company"].create({"name": "Test Company"})
        cls.scope = cls.env["collective.agreement.scope"].create({"name": "Scope Test"})
        cls.official_pub = cls.env["collective.agreement.official.publication"].create(
            {"name": "Official Publication Test"}
        )
        cls.partner = cls.env["res.partner"].create(
            {"name": "Partner Test", "company_id": cls.company.id}
        )
        cls.agreement = cls.env["collective.agreement"].create(
            {
                "code": "AG001",
                "name": "Agreement Test",
                "scope_id": cls.scope.id,
                "publication_date": "2025-10-01",
                "end_date": "2025-12-31",
                "official_publication_id": cls.official_pub.id,
                "state": "draft",
                "active": True,
                "company_id": cls.company.id,
                "partner_ids": [(6, 0, [cls.partner.id])],
            }
        )

    def test_active_partner_filter(self):
        other_company = self.env["res.company"].create({"name": "Other Company"})
        other_partner = self.env["res.partner"].create(
            {"name": "Partner Other", "company_id": other_company.id}
        )
        agreement = self.env["collective.agreement"].create(
            {
                "code": "AG003",
                "name": "Agreement Valid Partners",
                "scope_id": self.scope.id,
                "publication_date": "2025-10-01",
                "end_date": "2025-12-31",
                "official_publication_id": self.official_pub.id,
                "company_id": self.company.id,
                "partner_ids": [(6, 0, [self.partner.id])],
            }
        )
        self.assertIn(self.partner, agreement.partner_ids)
        self.assertNotIn(other_partner, agreement.partner_ids)

    def test_compute_collective_agreement_count(self):
        self.env["collective.agreement"].create(
            {
                "code": "AG002",
                "name": "Second Agreement",
                "scope_id": self.scope.id,
                "publication_date": "2025-11-01",
                "end_date": "2025-12-31",
                "official_publication_id": self.official_pub.id,
                "state": "draft",
                "active": True,
                "company_id": self.company.id,
                "partner_ids": [(6, 0, [self.partner.id])],
            }
        )
        self.assertEqual(self.partner.collective_agreement_count, 2)

    def test_action_view_collective_agreements(self):
        action = self.partner.action_view_collective_agreements()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "collective.agreement")
        self.assertIn(
            ("partner_ids", "in", [self.partner.id]),
            action["domain"],
        )
        self.assertEqual(
            action["context"]["partner_id"],
            self.partner.id,
        )
        self.assertEqual(
            action["context"]["default_partner_id"],
            self.partner.id,
        )

    def test_assign_wizard_adds_agreement_to_partner(self):
        partner = self.env["res.partner"].create(
            {"name": "Wizard Partner", "company_id": self.company.id}
        )
        agreement = self.env["collective.agreement"].create(
            {
                "code": "AG_WZ_01",
                "name": "Wizard Agreement",
                "scope_id": self.scope.id,
                "publication_date": "2025-10-01",
                "end_date": "2025-12-31",
                "official_publication_id": self.official_pub.id,
                "active": True,
                "company_id": self.company.id,
            }
        )
        wizard = self.env["collective.agreement.assign.wizard"].create(
            {
                "partner_id": partner.id,
                "collective_agreement_ids": [(6, 0, [agreement.id])],
            }
        )
        wizard.action_assign()
        self.assertIn(agreement, partner.collective_agreement_ids)

    def test_action_unassign_from_partner(self):
        self.assertIn(self.agreement, self.partner.collective_agreement_ids)
        action = self.agreement.with_context(
            partner_id=self.partner.id
        ).action_unassign_from_partner()
        self.assertNotIn(self.agreement, self.partner.collective_agreement_ids)
        self.assertEqual(action["type"], "ir.actions.client")
        self.assertEqual(action["tag"], "reload")
