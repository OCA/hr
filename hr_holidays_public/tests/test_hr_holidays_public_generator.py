# Copyright 2018 elego Software Solutions GmbH - Yu Weng
# Copyright 2018 initOS GmbH - Nikolina Todorova
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestHrHolidaysPublicGenerator(TransactionCase):

    def setUp(self):
        super(TestHrHolidaysPublicGenerator, self).setUp()

        # Usefull models
        self.HrHolidaysPublicGenerator = \
            self.env['hr.holidays.public.generator']
        self.HrHolidaysPublicLine = self.env['hr.holidays.public.line']
        self.HrHolidaysPublic = self.env['hr.holidays.public']
        self.TestYear = 2118
        self.CountryId = self.ref('base.de')

        # Test Create Public Holidays for 2018
        wizard_data = {
            "year": self.TestYear,
            "country_id": self.CountryId
        }

        self.hr_holidays_public_generator = \
            self.HrHolidaysPublicGenerator.create(wizard_data)

    def test_copy_function_name_does_not_exists(self):
        def dummy():
            return True

        template_id = \
            self.HrHolidaysPublic.create({
                'year': self.TestYear,
                'country_id': self.CountryId
            }).id

        # Test Create Public Holidays for 2119 from 2119
        # with not existing function for the CountryId
        CountryId = self.ref('base.fr')
        TestYear = 2119
        wizard_data = {
            "year": TestYear,
            "country_id": CountryId,
            "template_id": template_id
        }
        hr_holidays_public_generator_copy = \
            self.HrHolidaysPublicGenerator.create(wizard_data)

        hr_holidays_public_generator_copy.onchange_template_id()

        with self.assertRaises(UserError):
            hr_holidays_public_generator_copy.action_run()

        setattr(
            hr_holidays_public_generator_copy,
            'action_copy_de_holidays',
            dummy)
        hr_holidays_public_generator_copy.action_run()

    def test_generate_function_name_does_not_exists(self):
        def dummy():
            return True

        # Test Generate Public Holidays for 2118
        # with not existing function for the CountryId
        CountryId = self.ref('base.fr')
        wizard_data = {
            "year": self.TestYear,
            "country_id": CountryId
        }
        hr_holidays_public_generator_generate = \
            self.HrHolidaysPublicGenerator.create(wizard_data)

        with self.assertRaises(UserError):
            hr_holidays_public_generator_generate.action_run()

        setattr(
            hr_holidays_public_generator_generate,
            'action_generate_fr_holidays',
            dummy)
        hr_holidays_public_generator_generate.action_run()
