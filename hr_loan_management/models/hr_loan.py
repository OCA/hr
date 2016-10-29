# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil import relativedelta
from datetime import datetime
from openerp import models, fields, api
from openerp.tools.translate import _
from openerp.addons import decimal_precision as dp
from openerp.exceptions import Warning as UserError

DATE_SELECTION = map(lambda x: [x, str(x)], range(1, 32))


class HrLoan(models.Model):
    _name = "hr.loan"
    _description = "Employee Loan"
    _inherit = ["mail.thread"]

    @api.multi
    @api.depends(
        "payment_schedule_ids",
        "payment_schedule_ids.principle_amount",
        "payment_schedule_ids.interest_amount"
    )
    def _compute_total(self):
        for loan in self:
            loan.total_principle_amount = 0.0
            loan.total_interest_amount = 0.0
            if loan.payment_schedule_ids:
                for schedule in loan.payment_schedule_ids:
                    loan.total_principle_amount += schedule.principle_amount
                    loan.total_interest_amount += schedule.interest_amount

    @api.multi
    @api.depends(
        "request_date",
        "date_payment",
        "realization_date")
    def _compute_first_payment_date(self):
        for loan in self:
            date_payment = loan.date_payment

            if loan.realization_date:
                anchor_date = datetime.strptime(
                    loan.date_realization, "%Y-%m-%d")
            else:
                anchor_date = datetime.strptime(loan.request_date, "%Y-%m-%d")

            loan.first_payment_date = anchor_date + \
                relativedelta.relativedelta(
                    day=date_payment, months=+1)

    @api.multi
    @api.depends(
        "move_line_header_id",
        "move_line_header_id.reconcile_id")
    def _compute_realization(self):
        for loan in self:
            loan.realized = False
            if not loan.move_line_header_id:
                continue
            if loan.move_line_header_id.reconcile_id:
                loan.realized = True

    @api.model
    def _default_employee_id(self):
        criteria = [
            ("user_id", "=", self.env.user.id),
        ]
        employee = self.env["hr.employee"].search(criteria, limit=1)
        return employee

    name = fields.Char(
        string="# Loan",
        required=True,
        default="/",
        readonly=True,
    )
    employee_id = fields.Many2one(
        string="Employee",
        comodel_name="hr.employee",
        required=True,
        default=_default_employee_id,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    request_date = fields.Date(
        string="Realization Request Date",
        required=True,
        default=fields.Date.today(),
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    date_realization = fields.Date(
        string="Realization Date",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    loan_type_id = fields.Many2one(
        string="Loan Type",
        comodel_name="hr.loan.type",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    currency_id = fields.Many2one(
        string="Currency",
        related="loan_type_id.currency_id",
        store=True,
        readonly=True,
    )
    loan_amount = fields.Float(
        string="Loan Amount",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        digits=dp.get_precision("Account"),
    )
    maximum_loan_amount = fields.Float(
        string="Maximum Loan Amount",
        related="loan_type_id.maximum_loan_amount",
        store=True,
        readonly=True,
        digits=dp.get_precision("Account"),
    )
    interest = fields.Float(
        string="Interest (p.a)",
        related="loan_type_id.interest_amount",
        store=True,
        readonly=True,
        required=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        digits=dp.get_precision("Account"),
    )
    maximum_installment_period = fields.Integer(
        string="Maximum Installment Period",
        related="loan_type_id.maximum_installment_period",
        store=True,
        readonly=True,
    )
    manual_loan_period = fields.Integer(
        string="Loan Period",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        required=True,
    )
    date_payment = fields.Selection(
        string="Date Payment",
        selection=DATE_SELECTION,
        required=True,
    )
    first_payment_date = fields.Date(
        string="First Payment Date",
        compute="_compute_first_payment_date",
        readonly=True,
        store=True,
    )
    total_principle_amount = fields.Float(
        string="Total Principle Amount",
        compute="_compute_total",
        store=True,
        digits=dp.get_precision("Account"),
    )
    total_interest_amount = fields.Float(
        string="Total Interest Amount",
        compute="_compute_total",
        store=True,
        digits=dp.get_precision("Account"),
    )
    realized = fields.Boolean(
        string="Realized",
        compute="_compute_realization",
        store=True,
    )
    payment_schedule_ids = fields.One2many(
        string="Payment Schedules",
        comodel_name="hr.loan.payment.schedule",
        inverse_name="loan_id",
    )
    confirm_date = fields.Datetime(
        string="Confirm Date",
        readonly=True,
    )
    confirm_uid = fields.Many2one(
        string="Confirm By",
        comodel_name="res.users",
        readonly=True,
    )
    approve_date = fields.Datetime(
        string="Approve Date",
        readonly=True,
    )
    approve_uid = fields.Many2one(
        string="Approve By",
        comodel_name="res.users",
        readonly=True,
    )
    realization_date = fields.Datetime(
        string="Realization Date",
        readonly=True,
    )
    realization_uid = fields.Many2one(
        string="Realized By",
        comodel_name="res.users",
        readonly=True,
    )
    done_date = fields.Date(
        string="Done Date",
        readonly=True,
    )
    done_uid = fields.Many2one(
        string="Done By",
        comodel_name="res.users",
        readonly=True,
    )
    cancel_date = fields.Date(
        string="Cancel Date",
        readonly=True,
    )
    cancel_uid = fields.Many2one(
        string="Cancel By",
        comodel_name="res.users",
        readonly=True,
    )
    manual_realization = fields.Boolean(
        string="Manual Realization",
    )
    move_receivable_id = fields.Many2one(
        string="Receivable Journal Entry",
        comodel_name="account.move",
        readonly=True,
    )
    move_line_header_id = fields.Many2one(
        string="Receivable Move Line Header",
        comodel_name="account.move.line",
        readonly=True,
    )
    state = fields.Selection(
        string="State",
        selection=[
            ("draft", "Draft"),
            ("confirm", "Waiting for Approval"),
            ("approve", "Waiting for Realization"),
            ("active", "Active"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        default="draft",
        required=True,
        readonly=True,
    )

    @api.multi
    @api.constrains("maximum_loan_amount", "loan_amount")
    def _check_loan_amount(self):
        for loan in self:
            if loan.loan_amount <= 0.0:
                strWarning = _("Loan amount has to be greater than 0")
                raise models.ValidationError(strWarning)

            if loan.loan_amount > loan.maximum_loan_amount:
                strWarning = _("Loan amount exceed maximum loan amount")
                raise models.ValidationError(strWarning)

    @api.multi
    @api.constrains("maximum_installment_period", "manual_loan_period")
    def _check_loan_period(self):
        for loan in self:
            if loan.manual_loan_period <= 0:
                strWarning = _("Loan period has to be greated than 0")
                raise models.ValidationError(strWarning)
            if loan.manual_loan_period > loan.maximum_installment_period:
                strWarning = _("Loan period exceed maximum installment period")
                raise models.ValidationError(strWarning)

    @api.multi
    def name_get(self):
        res = []
        for loan in self:
            if loan.name == "/":
                name = "*%s" % (loan.id)
            else:
                name = loan.name
            res.append((loan.id, name))
        return res

    @api.multi
    def unlink(self):
        for loan in self:
            strWarning = _("""You can not delete loan %s. \n
                         Loan can be deleted only on cancel state and
                         has not been assigned a
                         loan number""") % loan.display_name
            if (loan.state != "cancel" or
                    loan.name != "/") and \
                    not self.env.context.get("force_unlink", False):
                raise UserError(strWarning)
        return super(HrLoan, self).unlink()

    @api.multi
    def action_compute_payment(self):
        for loan in self:
            self._compute_payment()

    @api.multi
    def _compute_payment(self):
        self.ensure_one()
        obj_payment = self.env["hr.loan.payment.schedule"]
        obj_loan_type = self.env["hr.loan.type"]

        self.payment_schedule_ids.unlink()

        payment_datas = obj_loan_type._compute_interest(
            self.loan_amount,
            self.interest,
            self.manual_loan_period,
            self.first_payment_date,
            self.loan_type_id.interest_method)

        for payment_data in payment_datas:
            payment_data.update({"loan_id": self.id})
            obj_payment.create(payment_data)

    @api.multi
    def workflow_action_confirm(self):
        for loan in self:
            data = self._prepare_confirm_data()
            loan.write(data)

    @api.multi
    def workflow_action_approve(self):
        for loan in self:
            loan._compute_payment()
            data = self._prepare_approve_data()
            loan.write(data)
            loan._create_receivable_move()

    @api.multi
    def workflow_action_active(self):
        for loan in self:
            data = self._prepare_active_data()
            loan.write(data)

    @api.multi
    def workflow_action_done(self):
        for loan in self:
            data = self._prepare_done_data()
            loan.write(data)

    @api.multi
    def workflow_action_cancel(self):
        for loan in self:
            if not self._can_cancel():
                strWarning = _("Employee loan can only be cancelled on "
                               "draft, waiting for approval or "
                               "ready to be process state")
                raise models.ValidationError(strWarning)
            self._delete_receivable_move()
            data = self._prepare_cancel_data()
            loan.write(data)

    @api.multi
    def _prepare_confirm_data(self):
        self.ensure_one()
        return {
            "name": self._create_sequence(),
            "state": "confirm",
            "confirm_date": fields.datetime.now(),
            "confirm_uid": self.env.user.id,
        }

    @api.multi
    def _can_cancel(self):
        self.ensure_one()
        if self.state not in ("draft", "confirm", "approve"):
            return False
        else:
            return True

    @api.multi
    def _prepare_approve_data(self):
        self.ensure_one()
        data = {
            "state": "approve",
            "approve_date": fields.datetime.now(),
            "approve_uid": self.env.user.id,
        }
        if not self.date_realization:
            data.update({
                "date_realization": fields.datetime.now(),
            })
        return data

    @api.multi
    def _delete_receivable_move(self):
        self.ensure_one()
        if self.move_receivable_id:
            self.move_receivable_id.unlink()

    @api.multi
    def _create_receivable_move(self):
        self.ensure_one()
        obj_move = self.env[
            "account.move"]
        obj_line = self.env[
            "account.move.line"]

        move = obj_move.sudo().create(
            self._prepare_receivable_move())

        self.move_receivable_id = move

        header = obj_line.sudo().create(
            self._prepare_header_move_line())

        self.move_line_header_id = header

        for schedule in self.payment_schedule_ids:
            schedule._create_principle_receivable_move_line()

    @api.multi
    def _prepare_active_data(self):
        self.ensure_one()
        return {
            "state": "active",
            "date_realization": fields.datetime.now(),
            "realization_date": fields.datetime.now(),
            "realization_uid": self.env.user.id,
        }

    @api.multi
    def _prepare_done_data(self):
        self.ensure_one()
        return {
            "state": "done",
            "done_date": fields.datetime.now(),
            "done_uid": self.env.user.id,
        }

    @api.multi
    def _prepare_cancel_data(self):
        self.ensure_one()
        return {
            "state": "cancel",
            "cancel_date": fields.datetime.now(),
            "cancel_uid": self.env.user.id,
        }

    @api.multi
    def _create_sequence(self):
        self.ensure_one()
        return self.env["ir.sequence"].get("hr.loan")

    @api.multi
    def _prepare_receivable_move(self):
        self.ensure_one()
        obj_period = self.env["account.period"]
        res = {
            "name": "/",
            "journal_id": self.loan_type_id.journal_id.id,
            "date": self.date_realization,
            "ref": self.name,
            "period_id": obj_period.find(
                self.date_realization)[0].id,
        }
        return res

    @api.multi
    def _get_employee_home_address(self):
        self.ensure_one()
        strWarning = _(
            "Home addres not set for %s employee") % (self.employee_id.name)
        if not self.employee_id.address_home_id:
            raise UserError(strWarning)
        return self.employee_id.address_home_id

    @api.model
    def _prepare_header_move_line(self):
        self.ensure_one()
        name = _("%s loan realization") % (self.name)
        res = {
            "move_id": self.move_receivable_id.id,
            "name": name,
            "account_id": self.loan_type_id.account_realization_id.id,
            "debit": 0.0,
            "credit": self.total_principle_amount,
            "partner_id": self._get_employee_home_address().id,
        }
        return res


class HrLoanPaymentSchedule(models.Model):
    _name = "hr.loan.payment.schedule"
    _description = "Loan Payment Schedule"
    _order = "schedule_date, id"

    @api.multi
    @api.depends("principle_amount", "interest_amount")
    def _compute_installment(self):
        for payment in self:
            payment.installment_amount = payment.principle_amount + \
                payment.interest_amount

    @api.multi
    @api.depends(
        "principle_move_line_id",
        "principle_move_line_id.reconcile_id",
        "principle_move_line_id.reconcile_partial_id",
        "interest_move_line_id",
        "interest_move_line_id.reconcile_id",
        "interest_move_line_id.reconcile_partial_id",
    )
    def _compute_state(self):
        for payment in self:
            principle_move_line = payment.principle_move_line_id
            interest_move_line = payment.interest_move_line_id
            if not principle_move_line:
                payment.principle_payment_state = "unpaid"
            elif principle_move_line and \
                    not principle_move_line.reconcile_partial_id and \
                    not principle_move_line.reconcile_id:
                payment.principle_payment_state = "unpaid"
            elif principle_move_line.reconcile_partial_id:
                payment.principle_payment_state = "partial"
            elif principle_move_line.reconcile_id:
                payment.principle_payment_state = "paid"

            if not interest_move_line:
                payment.interest_payment_state = "unpaid"
            elif interest_move_line and \
                    not interest_move_line.reconcile_partial_id and \
                    not interest_move_line.reconcile_id:
                payment.interest_payment_state = "unpaid"
            elif interest_move_line.reconcile_partial_id:
                payment.interest_payment_state = "partial"
            elif interest_move_line.reconcile_id:
                payment.interest_payment_state = "paid"

    loan_id = fields.Many2one(
        string="# Loan",
        comodel_name="hr.loan",
        ondelete="cascade",
    )
    employee_id = fields.Many2one(
        string="Employee",
        comodel_name="hr.employee",
        related="loan_id.employee_id",
        store=True,
        readonly=True,
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        related="loan_id.currency_id",
        store=False,
        readonly=True,
    )
    schedule_date = fields.Date(
        string="Schedule Date",
        required=True,
    )
    principle_amount = fields.Float(
        string="Principle Amount",
        required=True,
        digits=dp.get_precision("Account"),
    )
    interest_amount = fields.Float(
        string="Interest Amount",
        required=True,
        digits=dp.get_precision("Account"),
    )
    installment_amount = fields.Float(
        string="Installment Amount",
        compute="_compute_installment",
        store=True,
        digits=dp.get_precision("Account"),
    )
    principle_payment_state = fields.Selection(
        string="Principle Payment State",
        selection=[
            ("unpaid", "Unpaid"),
            ("partial", "Partial Paid"),
            ("paid", "Paid"),
        ],
        compute="_compute_state",
        required=False,
        store=True,
    )
    interest_payment_state = fields.Selection(
        string="Interest Payment State",
        selection=[
            ("unpaid", "Unpaid"),
            ("partial", "Partial Paid"),
            ("paid", "Paid"),
        ],
        compute="_compute_state",
        required=False,
        store=True,
    )
    principle_move_line_id = fields.Many2one(
        string="Principle Move Line",
        comodel_name="account.move.line",
        readonly=True,
    )
    principle_move_id = fields.Many2one(
        string="Principle Move",
        related="principle_move_line_id.move_id",
        comodel_name="account.move",
    )
    interest_move_line_id = fields.Many2one(
        string="Interest Move Line",
        comodel_name="account.move.line",
        readonly=True,
    )
    interest_move_id = fields.Many2one(
        string="Interest Move",
        related="interest_move_line_id.move_id",
        comodel_name="account.move",
    )
    state = fields.Selection(
        string="State",
        selection=[
            ("draft", "Draft"),
            ("confirm", "Waiting for Approval"),
            ("approve", "Waiting for Realization"),
            ("active", "Active"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        readonly=True,
        related="loan_id.state",
        store=True,
    )

    @api.multi
    def name_get(self):
        res = []
        for schedule in self:
            name = "%s %s" % (
                schedule.loan_id.display_name, schedule.schedule_date)
            res.append((schedule.id, name))
        return res

    @api.multi
    def action_realize_interest(self, date_realization=False):
        for schedule in self:
            self._create_interest_receivable_move(date_realization)

    @api.multi
    def _prepare_interest_receivable_move(self, date_realization):
        self.ensure_one()
        if not date_realization:
            date_realization = datetime.now().strftime(
                "%Y-%m-%d")
        obj_period = self.env["account.period"]
        loan = self.loan_id
        res = {
            "name": "/",
            "journal_id": loan.loan_type_id.journal_id.id,
            "date": date_realization,
            "ref": loan.name,
            "period_id": obj_period.find(
                date_realization)[0].id,
        }
        return res

    @api.multi
    def _create_interest_receivable_move(self, date_realization):
        self.ensure_one()
        obj_move = self.env[
            "account.move"]
        obj_line = self.env[
            "account.move.line"]

        move = obj_move.sudo().create(
            self._prepare_interest_receivable_move(
                date_realization))

        line_receivable = obj_line.sudo().create(
            self._prepare_interest_receivable_move_line(
                move))

        self.interest_move_line_id = line_receivable

        obj_line.sudo().create(
            self._prepare_interest_income_move_line(
                move))

    @api.multi
    def _prepare_principle_receivable_move_line(self):
        self.ensure_one()
        loan = self.loan_id
        loan_type = loan.loan_type_id
        name = _("%s %s principle receivable") % (
            loan.name, self.schedule_date)
        res = {
            "move_id": loan.move_receivable_id.id,
            "name": name,
            "account_id": loan_type.account_principle_id.id,
            "debit": self.principle_amount,
            "credit": 0.0,
            "date_maturity": self.schedule_date,
            "partner_id": loan.employee_id.address_home_id.id,
        }
        return res

    @api.multi
    def _create_principle_receivable_move_line(self):
        self.ensure_one()
        line = self.env[
            "account.move.line"].sudo().create(
                self._prepare_principle_receivable_move_line())
        self.principle_move_line_id = line

    @api.multi
    def _prepare_interest_receivable_move_line(self, move):
        self.ensure_one()
        loan = self.loan_id
        loan_type = loan.loan_type_id
        name = _("%s %s interest receivable") % (loan.name, self.schedule_date)
        res = {
            "move_id": move.id,
            "name": name,
            "account_id": loan_type.account_interest_id.id,
            "debit": self.interest_amount,
            "credit": 0.0,
            "date_maturity": self.schedule_date,
            "partner_id": loan._get_employee_home_address().id,
        }
        return res

    @api.multi
    def _prepare_interest_income_move_line(self, move):
        self.ensure_one()
        loan = self.loan_id
        loan_type = loan.loan_type_id
        name = _("%s %s interest income") % (loan.name, self.schedule_date)
        res = {
            "move_id": move.id,
            "name": name,
            "account_id": loan_type.account_interest_income_id.id,
            "credit": self.interest_amount,
            "debit": 0.0,
            "date_maturity": self.schedule_date,
            "partner_id": self.loan_id.employee_id.address_home_id.id,
        }
        return res
