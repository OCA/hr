# Copyright 2025 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import fields
from odoo.exceptions import ValidationError
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

        today = fields.Date.today()

        cls.agreement = cls.env["collective.agreement"].create(
            {
                "code": "AG001",
                "name": "Agreement Test",
                "scope_id": cls.scope.id,
                "publication_date": today,
                "end_date": today + timedelta(days=30),
                "official_publication_id": cls.official_pub.id,
                "state": "draft",
                "company_id": cls.company.id,
                "partner_ids": [(6, 0, [cls.partner.id])],
            }
        )

    def test_create_collective_agreement(self):
        self.assertEqual(self.agreement.code, "AG001")
        self.assertEqual(self.agreement.state, "draft")
        self.assertIn(self.partner, self.agreement.partner_ids)

    def test_check_end_date(self):
        today = fields.Date.today()

        with self.assertRaises(ValidationError):
            self.env["collective.agreement"].create(
                {
                    "code": "AG002",
                    "name": "Agreement Invalid Date",
                    "scope_id": self.scope.id,
                    "publication_date": today,
                    "end_date": today - timedelta(days=1),
                    "official_publication_id": self.official_pub.id,
                    "company_id": self.company.id,
                }
            )

    def test_copy_collective_agreement(self):
        self.agreement.action_activate_agreement()
        copied_agreement = self.agreement.copy()
        self.assertNotEqual(self.agreement.id, copied_agreement.id)
        self.assertEqual(
            copied_agreement.code,
            f"{self.agreement.code} (copy)",
        )
        self.assertEqual(
            copied_agreement.name,
            f"{self.agreement.name} (copy)",
        )
        self.assertEqual(copied_agreement.state, "draft")
        self.assertEqual(
            copied_agreement.scope_id,
            self.agreement.scope_id,
        )
        self.assertEqual(
            copied_agreement.company_id,
            self.agreement.company_id,
        )

    def test_action_activate_agreement(self):
        self.agreement.action_activate_agreement()
        self.assertEqual(self.agreement.state, "active")

    def test_action_activate_agreement_expired(self):
        today = fields.Date.today()

        expired_agreement = self.env["collective.agreement"].create(
            {
                "code": "AG003",
                "name": "Expired Agreement",
                "scope_id": self.scope.id,
                "publication_date": today - timedelta(days=60),
                "end_date": today - timedelta(days=1),
                "official_publication_id": self.official_pub.id,
                "state": "draft",
                "company_id": self.company.id,
            }
        )

        with self.assertRaises(ValidationError):
            expired_agreement.action_activate_agreement()

    def test_action_finish(self):
        self.agreement.state = "active"
        self.agreement.action_finish()
        self.assertEqual(self.agreement.state, "finished")

    def test_action_cancel(self):
        self.agreement.action_cancel()
        self.assertEqual(self.agreement.state, "cancelled")

    def test_action_draft(self):
        self.agreement.action_cancel()
        self.assertEqual(self.agreement.state, "cancelled")
        self.agreement.action_draft()
        self.assertEqual(self.agreement.state, "draft")

    def test_action_update_states_finish_expired(self):
        today = fields.Date.today()
        expired_agreement = self.env["collective.agreement"].create(
            {
                "code": "AG004",
                "name": "Expired Agreement 2",
                "scope_id": self.scope.id,
                "publication_date": today - timedelta(days=60),
                "end_date": today - timedelta(days=1),
                "official_publication_id": self.official_pub.id,
                "state": "active",
                "company_id": self.company.id,
            }
        )
        self.env["collective.agreement"].action_update_states()
        expired_agreement.invalidate_recordset()
        self.assertEqual(expired_agreement.state, "finished")

    def test_action_update_states_activate_draft(self):
        today = fields.Date.today()
        draft_agreement = self.env["collective.agreement"].create(
            {
                "code": "AG005",
                "name": "Draft Agreement",
                "scope_id": self.scope.id,
                "publication_date": today,
                "end_date": today + timedelta(days=10),
                "official_publication_id": self.official_pub.id,
                "state": "draft",
                "company_id": self.company.id,
            }
        )
        self.env["collective.agreement"].action_update_states()
        draft_agreement.invalidate_recordset()
        self.assertEqual(draft_agreement.state, "active")
