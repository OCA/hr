# Copyright 2018-2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from unittest import mock
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests import common

module_ns = 'odoo.addons.hr_holidays_accrual_advanced'
hr_leave_allocation_class = (
    module_ns + '.models.hr_leave_allocation.HrLeaveAllocation'
)
_get_date_from = hr_leave_allocation_class + '._get_date_from'
_get_date_to = hr_leave_allocation_class + '._get_date_to'


class TestHrHolidaysAccrualAdvanced(common.TransactionCase):

    def setUp(self):
        super().setUp()

        self.today = fields.Date.today()
        self.now = datetime.combine(
            fields.Date.today(),
            datetime.min.time()
        )
        self.Employee = self.env['hr.employee']
        self.SudoEmployee = self.Employee.sudo()
        self.LeaveType = self.env['hr.leave.type']
        self.SudoLeaveType = self.LeaveType.sudo()
        self.LeaveAllocation = self.env['hr.leave.allocation']
        self.SudoLeaveAllocation = self.LeaveAllocation.sudo()
        self.Leave = self.env['hr.leave']
        self.SudoLeave = self.Leave.sudo()
        self.Calculator = self.env[
            'hr.leave.allocation.accrual.calculator'
        ]
        self.SudoCalculator = self.Calculator.sudo()
        self.ResourceCalendar = self.env['resource.calendar']
        self.SudoResourceCalendar = self.ResourceCalendar.sudo()
        self.Calculator = self.env['hr.leave.allocation.accrual.calculator']

    def test_allocation_1(self):
        leave_type = self.SudoLeaveType.create({
            'name': 'Leave Type #1',
            'allocation_type': 'fixed',
        })
        employee = self.SudoEmployee.create({
            'name': 'Employee #1',
        })
        allocation = self.SudoLeaveAllocation.create({
            'holiday_type': 'employee',
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'state': 'validate',
            'accrual': True,
            'date_from': (
                self.now - relativedelta(years=3)
            ),
            'date_to': (
                self.now - relativedelta(years=1)
            ),
        })

        allocation.action_recalculate_accrual_allocations()
        self.assertEqual(allocation.number_of_days, 40.0)

        allocation.action_recalculate_accrual_allocations_all()
        self.assertEqual(allocation.number_of_days, 40.0)

        self.SudoLeaveAllocation._update_accrual()
        self.assertEqual(allocation.number_of_days, 40.0)

    def test_allocation_2(self):
        leave_type = self.SudoLeaveType.create({
            'name': 'Leave Type #2',
            'allocation_type': 'fixed',
        })
        employee = self.SudoEmployee.create({
            'name': 'Employee #2',
        })
        allocation = self.SudoLeaveAllocation.create({
            'holiday_type': 'employee',
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'state': 'validate',
            'accrual': True,
            'accrual_method': 'period_end',
        })

        date_from = (
            self.now - relativedelta(years=1) + relativedelta(days=1)
        )
        with mock.patch(_get_date_from, return_value=date_from):
            allocation._update_accrual_allocation()

        self.assertEqual(allocation.number_of_days, 0.0)

    def test_allocation_3(self):
        leave_type = self.SudoLeaveType.create({
            'name': 'Leave Type #3',
            'allocation_type': 'fixed',
        })
        employee = self.SudoEmployee.create({
            'name': 'Employee #3',
        })
        allocation = self.SudoLeaveAllocation.create({
            'holiday_type': 'employee',
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'state': 'validate',
            'accrual': True,
            'accrual_method': 'period_end',
        })

        date_from = (
            self.now - relativedelta(years=1, days=1)
        )
        with mock.patch(_get_date_from, return_value=date_from):
            allocation._update_accrual_allocation()

        self.assertAlmostEqual(allocation.number_of_days, 20.0, 0)

    def test_allocation_4(self):
        leave_type = self.SudoLeaveType.create({
            'name': 'Leave Type #4',
            'allocation_type': 'fixed',
        })
        employee = self.SudoEmployee.create({
            'name': 'Employee #4',
        })
        allocation = self.SudoLeaveAllocation.create({
            'holiday_type': 'employee',
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'state': 'validate',
            'accrual': True,
            'limit_carryover_days': True,
            'max_carryover_days': 5.0,
        })

        date_from = (
            self.now - relativedelta(years=1, days=1)
        )
        with mock.patch(_get_date_from, return_value=date_from):
            allocation._update_accrual_allocation()

        self.assertAlmostEqual(allocation.number_of_days, 5.0, 0)

    def test_allocation_5(self):
        leave_type = self.SudoLeaveType.create({
            'name': 'Leave Type #5',
            'allocation_type': 'fixed',
        })
        employee = self.SudoEmployee.create({
            'name': 'Employee #5',
        })
        allocation = self.SudoLeaveAllocation.create({
            'holiday_type': 'employee',
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'state': 'validate',
            'accrual': True,
            'limit_carryover_days': True,
            'max_carryover_days': 0.0,
        })

        date_from = (
            self.now - relativedelta(years=1, days=1)
        )
        with mock.patch(_get_date_from, return_value=date_from):
            allocation._update_accrual_allocation()

        self.assertAlmostEqual(allocation.number_of_days, 0.0, 0)

    def test_allocation_6(self):
        leave_type = self.SudoLeaveType.create({
            'name': 'Leave Type #6',
            'allocation_type': 'fixed',
        })
        employee = self.SudoEmployee.create({
            'name': 'Employee #6',
        })
        allocation = self.SudoLeaveAllocation.create({
            'holiday_type': 'employee',
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'state': 'validate',
            'accrual': True,
            'limit_carryover_days': True,
            'max_carryover_days': 5.0,
            'limit_accumulated_days': True,
            'max_accumulated_days': 20.0,
        })

        date_from = (
            self.now - relativedelta(years=10, days=1)
        )
        with mock.patch(_get_date_from, return_value=date_from):
            allocation._update_accrual_allocation()

        self.assertAlmostEqual(allocation.number_of_days, 5.0, 0)

    def test_allocation_7(self):
        leave_type = self.SudoLeaveType.create({
            'name': 'Leave Type #7',
            'allocation_type': 'fixed',
        })
        employee = self.SudoEmployee.create({
            'name': 'Employee #7',
        })
        allocation = self.SudoLeaveAllocation.create({
            'holiday_type': 'employee',
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'state': 'validate',
            'accrual': True,
            'limit_carryover_days': True,
            'max_carryover_days': 5.0,
            'limit_accumulated_days': True,
            'max_accumulated_days': 1.0,
        })

        date_from = (
            self.now - relativedelta(years=10, days=1)
        )
        with mock.patch(_get_date_from, return_value=date_from):
            allocation._update_accrual_allocation()

        self.assertAlmostEqual(allocation.number_of_days, 1.0, 0)

    def test_allocation_8(self):
        leave_type = self.SudoLeaveType.create({
            'name': 'Leave Type #8',
            'allocation_type': 'fixed',
            'validity_start': False,
        })
        employee = self.SudoEmployee.create({
            'name': 'Employee #8',
        })
        allocation = self.SudoLeaveAllocation.create({
            'holiday_type': 'employee',
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'state': 'validate',
            'accrual': True,
        })
        unpaid_leave_type = self.SudoLeaveType.create({
            'name': 'Leave Type #8 (unpaid)',
            'allocation_type': 'no',
            'unpaid': True,
            'validity_start': False,
        })
        unpaid_from = self.now - relativedelta(years=1)
        unpaid_to = self.now - relativedelta(months=6)
        unpaid_leave = self.SudoLeave.create({
            'name': 'Leave #8 (unpaid)',
            'employee_id': employee.id,
            'holiday_status_id': unpaid_leave_type.id,
            'date_from': unpaid_from,
            'date_to': unpaid_to,
        })
        unpaid_leave._onchange_leave_dates()
        unpaid_leave.action_approve()

        date_from = (
            self.now - relativedelta(years=1, days=1)
        )
        with mock.patch(_get_date_from, return_value=date_from):
            allocation._update_accrual_allocation()

        self.assertAlmostEqual(allocation.number_of_days, 10.0, 0)

    def test_allocation_9(self):
        leave_type = self.SudoLeaveType.create({
            'name': 'Leave Type #9',
            'allocation_type': 'fixed',
        })
        employee = self.SudoEmployee.create({
            'name': 'Employee #9',
        })
        allocation = self.SudoLeaveAllocation.create({
            'holiday_type': 'employee',
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'state': 'validate',
            'accrual': True,
        })

        allocation._update_accrual_allocation()

        self.assertEqual(allocation.number_of_days, 0)

    def test_allocation_10(self):
        leave_type = self.SudoLeaveType.create({
            'name': 'Leave Type #10',
            'allocation_type': 'fixed',
        })
        employee = self.SudoEmployee.create({
            'name': 'Employee #10',
        })
        allocation = self.SudoLeaveAllocation.create({
            'holiday_type': 'employee',
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'state': 'validate',
            'accrual': True,
            'limit_carryover_days': True,
            'max_carryover_days': 5.0,
            'limit_accrued_days': True,
            'max_accrued_days': 20.0,
            'limit_accumulated_days': True,
            'max_accumulated_days': 20.0,
        })

        date_from = (
            self.now - relativedelta(years=10) - relativedelta(days=1)
        )
        with mock.patch(_get_date_from, return_value=date_from):
            allocation._update_accrual_allocation()

        self.assertAlmostEqual(allocation.number_of_days, 5.0, 0)

    def test_allocation_11(self):
        leave_type = self.SudoLeaveType.create({
            'name': 'Leave Type #11',
            'allocation_type': 'fixed',
        })
        employee = self.SudoEmployee.create({
            'name': 'Employee #11',
        })
        allocation = self.SudoLeaveAllocation.create({
            'holiday_type': 'employee',
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'state': 'validate',
            'accrual': True,
        })

        date_from = (
            self.now - relativedelta(years=1)
        )
        with mock.patch(_get_date_from, return_value=date_from):
            allocation._update_accrual_allocation()

        allocation.limit_accumulated_days = True
        allocation.max_accumulated_days = 5.5

        self.assertEqual(allocation.accrual_limit, 6)

        allocation.limit_accumulated_days = False

        self.assertEqual(allocation.accrual_limit, 0)

    def test_allocation_12(self):
        leave_type = self.SudoLeaveType.create({
            'name': 'Leave Type #12',
            'allocation_type': 'fixed',
        })
        employee = self.SudoEmployee.create({
            'name': 'Employee #12',
        })
        allocation = self.SudoLeaveAllocation.create({
            'holiday_type': 'employee',
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'accrual': True,
        })

        allocation.mode_company_id = employee.company_id
        allocation.holiday_type = 'company'

        self.assertEqual(allocation.accrual, False)

    def test_allocation_13(self):
        leave_type = self.SudoLeaveType.create({
            'name': 'Leave Type #13',
            'allocation_type': 'fixed',
        })
        employee = self.SudoEmployee.create({
            'name': 'Employee #13',
        })
        allocation = self.SudoLeaveAllocation.create({
            'holiday_type': 'company',
            'mode_company_id': employee.company_id.id,
            'holiday_status_id': leave_type.id,
            'accrual': True,
        })

        self.assertEqual(allocation.accrual, False)

    def test_allocation_14(self):
        leave_type = self.SudoLeaveType.create({
            'name': 'Leave Type #14',
            'allocation_type': 'fixed',
        })
        employee = self.SudoEmployee.create({
            'name': 'Employee #14',
        })
        allocation = self.SudoLeaveAllocation.create({
            'holiday_type': 'employee',
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'accrual': True,
        })

        allocation.mode_company_id = employee.company_id
        allocation.holiday_type = 'company'

        self.assertEqual(allocation.accrual, False)

    def test_allocation_15(self):
        leave_type = self.SudoLeaveType.create({
            'name': 'Leave Type #15',
            'allocation_type': 'fixed',
        })
        employee = self.SudoEmployee.create({
            'name': 'Employee #15',
        })
        allocation = self.SudoLeaveAllocation.create({
            'holiday_type': 'employee',
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'state': 'validate',
            'accrual': True,
            'limit_accrued_days': True,
            'max_accrued_days': 5.0,
        })

        date_from = (
            self.now - relativedelta(years=10)
        )
        with mock.patch(_get_date_from, return_value=date_from):
            allocation._update_accrual_allocation()

        self.assertAlmostEqual(allocation.number_of_days, 50.0, 0)

    def test_allocation_16(self):
        leave_type = self.SudoLeaveType.create({
            'name': 'Leave Type #16',
            'allocation_type': 'fixed',
        })
        employee = self.SudoEmployee.create({
            'name': 'Employee #16',
        })
        allocation = self.SudoLeaveAllocation.create({
            'holiday_type': 'employee',
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'state': 'validate',
            'accrual': True,
            'date_from': self.now - relativedelta(years=2),
            'date_to': self.now - relativedelta(years=1),
        })

        allocation._update_accrual_allocation()

        self.assertAlmostEqual(allocation.number_of_days, 20.0, 0)

    def test_allocation_17(self):
        leave_type = self.SudoLeaveType.create({
            'name': 'Leave Type #17',
            'allocation_type': 'fixed',
        })
        employee = self.SudoEmployee.create({
            'name': 'Employee #17',
        })
        allocation = self.SudoLeaveAllocation.create({
            'holiday_type': 'employee',
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'state': 'validate',
            'accrual': True,
        })

        calculator = self.SudoCalculator.with_context(
            active_id=allocation.id
        ).create({
            'date': self.now,
        })

        calculator.date = self.today + relativedelta(years=10)

        date_from = (
            self.now - relativedelta(years=10)
        )
        with mock.patch(_get_date_from, return_value=date_from):
            calculator._onchange()

        self.assertAlmostEqual(calculator.balance, 400.0, 0)

    def test_allocation_18(self):
        leave_type = self.SudoLeaveType.create({
            'name': 'Leave Type #18',
            'allocation_type': 'fixed',
        })
        employee = self.SudoEmployee.create({
            'name': 'Employee #17',
        })
        allocation = self.SudoLeaveAllocation.create({
            'holiday_type': 'employee',
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'state': 'validate',
            'accrual': True,
        })

        date_from = (
            self.now + relativedelta(years=10)
        )
        with mock.patch(_get_date_from, return_value=date_from):
            allocation._update_accrual_allocation()

        self.assertAlmostEqual(allocation.number_of_days, 0.0, 0)

    def test_allocation_19(self):
        leave_type = self.SudoLeaveType.create({
            'name': 'Leave Type #19',
            'allocation_type': 'fixed',
            'validity_start': False,
        })
        employee = self.SudoEmployee.create({
            'name': 'Employee #19',
        })
        allocation = self.SudoLeaveAllocation.create({
            'holiday_type': 'employee',
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'state': 'validate',
            'accrual': True,
            'accrual_method': 'period_start',
        })

        date_from = (
            self.now - relativedelta(days=1)
        )
        with mock.patch(_get_date_from, return_value=date_from):
            allocation._update_accrual_allocation()

        self.assertAlmostEqual(allocation.number_of_days, 20.0, 0)

    def test_allocation_20(self):
        leave_type = self.SudoLeaveType.create({
            'name': 'Leave Type #20',
            'allocation_type': 'fixed',
            'validity_start': False,
        })
        employee = self.SudoEmployee.create({
            'name': 'Employee #20',
        })
        allocation = self.SudoLeaveAllocation.create({
            'holiday_type': 'employee',
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'state': 'validate',
            'accrual': True,
            'limit_accumulated_days': True,
            'max_accumulated_days': 20.0,
        })

        date_from = (
            self.now - relativedelta(years=1)
        )
        with mock.patch(_get_date_from, return_value=date_from):
            allocation._update_accrual_allocation()
        self.assertAlmostEqual(allocation.number_of_days, 20.0, 0)
        self.assertEqual(len(allocation.accruement_ids), 1)

        leave_from = self.now - relativedelta(days=10)
        leave_to = self.now
        leave = self.SudoLeave.create({
            'name': 'Leave #20',
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'date_from': leave_from,
            'date_to': leave_to,
            'number_of_days': 10.0,
        })

        with mock.patch(_get_date_from, return_value=date_from):
            allocation._update_accrual_allocation()
        self.assertAlmostEqual(allocation.number_of_days, 20.0, 0)
        self.assertEqual(len(allocation.accruement_ids), 1)

        leave.action_approve()
        with mock.patch(_get_date_from, return_value=date_from):
            allocation._update_accrual_allocation()
        self.assertAlmostEqual(allocation.number_of_days, 20.0, 0)
        self.assertEqual(len(allocation.accruement_ids), 2)

    def test_allocation_21(self):
        leave_type = self.SudoLeaveType.create({
            'name': 'Leave Type #21',
            'allocation_type': 'fixed',
        })
        employee = self.SudoEmployee.create({
            'name': 'Employee #21',
        })
        allocation = self.SudoLeaveAllocation.create({
            'holiday_type': 'employee',
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'state': 'validate',
            'accrual': True,
            'limit_accumulated_days': True,
            'max_accumulated_days': 10.0,
        })

        date_from = (
            self.now - relativedelta(years=1) - relativedelta(months=1)
        )
        with mock.patch(_get_date_from, return_value=date_from):
            allocation._update_accrual_allocation()
        self.assertAlmostEqual(allocation.number_of_days, 10.0, 0)
        self.assertEqual(len(allocation.accruement_ids), 4)

    def test_allocation_22(self):
        leave_type = self.SudoLeaveType.create({
            'name': 'Leave Type #22',
            'allocation_type': 'fixed',
        })
        employee = self.SudoEmployee.create({
            'name': 'Employee #22',
        })
        allocation = self.SudoLeaveAllocation.create({
            'holiday_type': 'employee',
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'state': 'validate',
            'accrual': True,
        })

        date_from = (
            self.now - relativedelta(years=1) - relativedelta(days=1)
        )
        with mock.patch(_get_date_from, return_value=date_from):
            accruements, number_of_days = allocation._calculate_accrued_amount(
                datetime.combine(
                    (self.now - relativedelta(months=6)).date(),
                    datetime.min.time()
                )
            )
        self.assertAlmostEqual(number_of_days, 10.0, 0)
        self.assertEqual(len(accruements), 1)

    def test_allocation_23(self):
        leave_type = self.SudoLeaveType.create({
            'name': 'Leave Type #23',
            'allocation_type': 'fixed',
            'validity_start': False,
        })
        calendar = self.SudoResourceCalendar.create({
            'name': 'Calendar #23',
        })
        calendar.write({
            'global_leave_ids': [
                (0, False, {
                    'name': 'Global Leave #23',
                    'date_from': self.now - relativedelta(days=7),
                    'date_to': self.now,
                }),
            ],
        })
        employee = self.SudoEmployee.create({
            'name': 'Employee #23',
            'resource_calendar_id': calendar.id,
        })
        allocation = self.SudoLeaveAllocation.create({
            'holiday_type': 'employee',
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'state': 'validate',
            'accrual': True,
            'limit_accumulated_days': True,
            'max_accumulated_days': 20.0,
        })

        date_from = (
            self.now - relativedelta(years=1)
        )
        with mock.patch(_get_date_from, return_value=date_from):
            allocation._update_accrual_allocation()
        self.assertAlmostEqual(allocation.number_of_days, 20.0, 0)
        self.assertEqual(len(allocation.accruement_ids), 1)

        leave = self.SudoLeave.create({
            'name': 'Leave #23',
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'date_from': self.now - relativedelta(days=14),
            'date_to': self.now,
        })
        leave._onchange_leave_dates()
        leave.action_approve()
        self.assertEqual(leave.number_of_days, 5)

        with mock.patch(_get_date_from, return_value=date_from):
            allocation._update_accrual_allocation()
        self.assertAlmostEqual(allocation.number_of_days, 20.0, 0)
        self.assertAlmostEqual(sum(map(
            lambda x: x.days_accrued,
            allocation.accruement_ids
        )), 15.0, 0)
        self.assertEqual(len(allocation.accruement_ids), 2)

    def test_allocation_24(self):
        leave_type = self.SudoLeaveType.create({
            'name': 'Leave Type #24',
            'allocation_type': 'fixed',
            'validity_start': False,
        })
        employee = self.SudoEmployee.create({
            'name': 'Employee #24',
        })
        allocation = self.SudoLeaveAllocation.create({
            'holiday_type': 'employee',
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'state': 'validate',
            'accrual': True,
        })

        date_from = self.now - relativedelta(years=2)
        with mock.patch(_get_date_from, return_value=date_from):
            allocation._update_accrual_allocation()
        self.assertEqual(allocation.number_of_days, 40.0)

        leave = self.SudoLeave.create({
            'name': 'Leave #24',
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'date_from': (
                self.now - relativedelta(years=1) - relativedelta(days=7)
            ),
            'date_to': (
                self.now - relativedelta(years=1) + relativedelta(days=7)
            ),
        })
        leave._onchange_leave_dates()
        leave.action_approve()
        self.assertEqual(leave.number_of_days, 10)

        with mock.patch(_get_date_from, return_value=date_from):
            accruements, number_of_days = allocation._calculate_accrued_amount(
                self.now
            )
        self.assertEqual(number_of_days, 40.0)
        self.assertEqual(sum(map(
            lambda x: x.days_accrued,
            accruements
        )), 30.0)

    def test_calculator(self):
        leave_type = self.SudoLeaveType.create({
            'name': 'Leave Type',
            'allocation_type': 'fixed',
        })
        employee = self.SudoEmployee.create({
            'name': 'Employee',
        })
        allocation = self.SudoLeaveAllocation.create({
            'holiday_type': 'employee',
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'state': 'validate',
            'accrual': True,
            'date_from': (
                self.now - relativedelta(years=3)
            ),
            'date_to': (
                self.now - relativedelta(years=1)
            ),
        })

        calculator = self.Calculator.with_context({
            'active_id': allocation.id,
        }).new()
        calculator._onchange()
        self.assertEqual(calculator.accrued, 0.0)
        self.assertEqual(calculator.balance, 0.0)

        calculator.date = self.today
        calculator._onchange()
        self.assertEqual(calculator.accrued, 40.0)
        self.assertEqual(calculator.balance, 40.0)
