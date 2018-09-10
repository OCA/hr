# Copyright 2018 elego Software Solutions GmbH - Yu Weng
# Copyright 2018 initOS GmbH - Nikolina Todorova
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.hr_holidays_public_generator_de.tests.common import \
    TestHrHolidaysPublicGenerator
from odoo.exceptions import UserError


class TestHrHolidaysPublicGenerator(TestHrHolidaysPublicGenerator):

    def test_action_generate_de_holidays(self):
        self.hr_holidays_public_generator.action_run()

        hr_holiday_public = \
            self.HrHolidaysPublic.search([
                ('year', '=', self.TestYear),
                ('country_id', '=', self.CountryId)
            ])
        if not hr_holiday_public:
            hr_holiday_public = None

        self.assertIsNotNone(hr_holiday_public)

        if hr_holiday_public:
            line_ids = hr_holiday_public.line_ids
            if not line_ids:
                line_ids = None
            self.assertIsNotNone(line_ids)

    def test_action_copy_de_holidays(self):
        self.hr_holidays_public_generator.action_generate_de_holidays()
        template_id = \
            self.HrHolidaysPublic.search([
                ('year', '=', self.TestYear),
                ('country_id', '=', self.CountryId)
            ])[0].id

        # Test Create Public Holidays for 2019 from 2019
        TestYear = 2019
        wizard_data = {
            "year": TestYear,
            "country_id": self.CountryId,
            "template_id": template_id
        }

        hr_holidays_public_generator_copy = \
            self.HrHolidaysPublicGenerator.create(wizard_data)

        hr_holidays_public_generator_copy.action_run()

        hr_holiday_public = \
            self.HrHolidaysPublic.search([
                ('year', '=', TestYear),
                ('country_id', '=', self.CountryId)
            ])
        if not hr_holiday_public:
            hr_holiday_public = None

        self.assertIsNotNone(hr_holiday_public)

        if hr_holiday_public:
            line_ids = hr_holiday_public.line_ids
            if not line_ids:
                line_ids = None
            self.assertIsNotNone(line_ids)

    def test_copy_function_name_does_not_exists(self):
        self.hr_holidays_public_generator.action_generate_de_holidays()
        template_id = \
            self.HrHolidaysPublic.search([
                ('year', '=', self.TestYear),
                ('country_id', '=', self.CountryId)
            ])[0].id

        # Test Create Public Holidays for 2019 from 2019
        # with not existing function for the CountryId
        CountryId = self.ref('base.fr')
        TestYear = 2019
        wizard_data = {
            "year": TestYear,
            "country_id": CountryId,
            "template_id": template_id
        }
        hr_holidays_public_generator_copy = \
            self.HrHolidaysPublicGenerator.create(wizard_data)

        with self.assertRaises(UserError):
            hr_holidays_public_generator_copy.action_run()

    def test_generate_function_name_does_not_exists(self):
        # Test Generate Public Holidays for 2018
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

    def test_copy_to_same_year_error(self):
        self.hr_holidays_public_generator.action_generate_de_holidays()
        template_id = \
            self.HrHolidaysPublic.search([
                ('year', '=', self.TestYear),
                ('country_id', '=', self.CountryId)
            ])[0].id
        wizard_data = {
            "year": self.TestYear,
            "country_id": self.CountryId,
            "template_id": template_id
        }
        hr_holidays_public_generator_copy = \
            self.HrHolidaysPublicGenerator.create(wizard_data)

        with self.assertRaises(UserError):
            hr_holidays_public_generator_copy.action_run()
