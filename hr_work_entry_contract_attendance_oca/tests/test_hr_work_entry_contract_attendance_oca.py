# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo.tests.common import TransactionCase


class TestHRWorkEntryContractAttendanceOCA(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    # TODO: test that a work entry is created when an attendance (with
    # check_out set) is created

    # TODO: test that a work entry is created when an attendance with
    # check_out not set is modified by setting its check_out field

    # TODO: test that a work entry is updated when an attendance is modified

    # TODO: test that modifying an attendance linked to a validated work entry
    # raises an error

    # TODO: test that modifying an attendance linked to multiple work entries
    # updates all work entries accordingly
