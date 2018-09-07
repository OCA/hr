#  Copyright 2018 elego Software Solutions GmbH - Yu Weng
#  Copyright 2018 initOS GmbH - Nikolina Todorova
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestHrHolidaysPublicGenerator(common.TransactionCase):

    def setUp(self):
        super(TestHrHolidaysPublicGenerator, self).setUp()

        # Usefull models
        self.HrHolidaysPublicGenerator = \
            self.env['hr.holidays.public.generator']
        self.HrHolidaysPublicLine = self.env['hr.holidays.public.line']
        self.HrHolidaysPublic = self.env['hr.holidays.public']
        self.TestYear = 2018
        self.CountryId = self.ref('base.de')

        # Test Create Public Holidays for 2018
        wizard_data = {
            "year": self.TestYear,
            "country_id": self.CountryId
        }

        self.hr_holidays_public_generator = \
            self.HrHolidaysPublicGenerator.create(wizard_data)
