# copyright  2017 Denis Leemann, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from dateutil.relativedelta import relativedelta

from odoo.exceptions import ValidationError
from odoo.tests import common
from odoo import fields


class TestHrEmployeeSeniority(common.TransactionCase):

    def setUp(self):
        super(TestHrEmployeeSeniority, self).setUp()
        self.employee_model = self.env['hr.employee']
        self.contract_model = self.env["hr.contract"]
        # Create an employees
        self.employee = self.employee_model.create({
            'name': 'Employee 1',
        })
        date_now = fields.Date.today()
        self.now = fields.Date.from_string(date_now)
        dt = relativedelta(months=6)
        self.six_months_ago = self.now - dt

        dt = relativedelta(years=1)
        self.one_year_ago = self.now - dt

        dt = relativedelta(years=2)
        self.two_year_ago = self.now - dt

        dt = relativedelta(years=3)
        self.three_year_ago = self.now - dt

        dt = relativedelta(years=1)
        self.one_year_in_future = self.now + dt

    def test_initial_employment_date_only_supplied(self):
        # if we are supplying only the initial employment date that should
        # be used to calculate service length
        self.employee.write({'initial_employment_date': self.one_year_ago})
        self.assertAlmostEqual(self.employee.length_of_service, 12.0)

    def test_contract_start_date_only_supplied(self):
        # initial employment date not supplied but we do have a contract
        # start date
        self.contract_model.create(
            {
                'employee_id': self.employee.id,
                'name': 'Contract 1',
                'date_start': self.one_year_ago,
                'date_end': self.one_year_in_future,
                'wage': 5000
            }
        )
        self.assertAlmostEqual(self.employee.length_of_service, 12.0)

    def test_inital_employment_before_first_contract_date(self):
        # initial employment date is supplied and we have a contract
        # however in this case the initial employment date is before that
        # of the first contract... we expect to use initial employment date
        self.contract_model.create(
            {
                'employee_id': self.employee.id,
                'name': 'Contract 1',
                'date_start': self.one_year_ago,
                'date_end': self.one_year_in_future,
                'wage': 5000
            }
        )
        self.employee.write({'initial_employment_date': self.two_year_ago})
        self.assertAlmostEqual(self.employee.length_of_service, 24.0)

        with self.assertRaises(ValidationError):
            self.employee.write({
                'initial_employment_date': self.six_months_ago
            })

    def test_multiple_contracts_with_no_interval(self):
        # multiple contracts
        self.contract_model.create(
            {
                'employee_id': self.employee.id,
                'name': 'Contract 1',
                'date_start': self.two_year_ago,
                'date_end': self.one_year_ago,
                'wage': 5000
            }
        )
        self.contract_model.create(
            {
                'employee_id': self.employee.id,
                'name': 'Contract 2',
                'date_start': self.one_year_ago,
                'date_end': self.now,
                'wage': 5000
            }
        )
        self.assertAlmostEqual(self.employee.length_of_service, 24.0)

    def test_multiple_contracts_with_interval(self):
        # contracts have breaks
        self.contract_model.create(
            {
                'employee_id': self.employee.id,
                'name': 'Contract 1',
                'date_start': self.three_year_ago,
                'date_end': self.two_year_ago,
                'wage': 5000
            }
        )
        self.contract_model.create(
            {
                'employee_id': self.employee.id,
                'name': 'Contract 2',
                'date_start': self.one_year_ago,
                'date_end': self.now,
                'wage': 5000
            }
        )
        self.assertAlmostEqual(self.employee.length_of_service, 24.0)

    def test_days_in_contract(self):
        # 3 Days contracts
        self.contract_model.create(
            {
                'employee_id': self.employee.id,
                'name': 'Contract 1',
                'date_start': '2017-01-01',
                'date_end': '2017-01-03',
                'wage': 5000
            }
        )
        self.assertAlmostEqual(self.employee.length_of_service, 0.0)
        # 2 months contract
        self.contract_model.create(
            {
                'employee_id': self.employee.id,
                'name': 'Contract 1',
                'date_start': '2016-11-01',
                'date_end': '2016-12-31',
                'wage': 5000
            }
        )
        self.assertAlmostEqual(self.employee.length_of_service, 2.0)
