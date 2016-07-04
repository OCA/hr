# -*- coding: utf-8 -*-
# © 2012 Odoo Canada
# © 2015 Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models, fields, api
from openerp.tools.translate import _
from openerp.exceptions import Warning as UserError


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.multi
    def _timesheet_mapping(self, timesheet_sheets, payslip, date_from,
                           date_to):
        """This function takes timesheet objects imported from the timesheet
        module and creates a dict of worked days to be created in the payslip.
        """
        # Create one worked days record for each timesheet sheet
        wd_model = self.env['hr.payslip.worked_days']
        uom_obj = self.env['product.uom']
        uom_hours = self.env.ref('product.product_uom_hour')
        for ts_sheet in timesheet_sheets:
            # Get formated date from the timesheet sheet
            date_from_formated = fields.Date.to_string(
                fields.Datetime.from_string(ts_sheet.date_from))
            number_of_hours = 0
            for ts in ts_sheet.timesheet_ids:
                if date_from <= ts.date <= date_to:
                    unit_amount = uom_obj._compute_qty_obj(
                        ts.product_uom_id,
                        ts.unit_amount, uom_hours)
                    number_of_hours += unit_amount

            if number_of_hours > 0:
                wd_model.create({
                    'name': _('Timesheet %s') % date_from_formated,
                    'number_of_hours': number_of_hours,
                    'contract_id': payslip.contract_id.id,
                    'code': 'TS',
                    'imported_from_timesheet': True,
                    'timesheet_sheet_id': ts_sheet.id,
                    'payslip_id': payslip.id,
                })

    @api.multi
    def import_worked_days(self):
        """This method retreives the employee's timesheets for a payslip period
        and creates worked days records from the imported timesheets
        """
        for payslip in self:

            date_from = payslip.date_from
            date_to = payslip.date_to

            # Delete old imported worked_days
            # The reason to delete these records is that the user may make
            # corrections to his timesheets and then reimport these.
            wd_model = self.env['hr.payslip.worked_days']
            wd_model.search(
                [('payslip_id', '=', payslip.id),
                 ('imported_from_timesheet', '=', True)]).unlink()

            # get timesheet sheets of employee
            criteria = [
                ('date_from', '>=', date_from),
                ('date_to', '<=', date_to),
                ('state', '=', 'done'),
                ('employee_id', '=', payslip.employee_id.id),
            ]
            ts_model = self.env['hr_timesheet_sheet.sheet']
            timesheet_sheets = ts_model.search(criteria)

            if not timesheet_sheets:
                raise UserError(
                    _("Sorry, but there is no approved Timesheets for the \
                    entire Payslip period"),
                )

            # The reason to call this method is for other modules to modify it.
            self._timesheet_mapping(
                timesheet_sheets,
                payslip,
                date_from,
                date_to
            )

    @api.multi
    def action_import_timesheet_activity(self):
        obj_uom = self.env["product.uom"]
        obj_timesheet_line = self.env["hr.analytic.timesheet"]
        obj_worked_days = self.env["hr.payslip.worked_days"]
        obj_rule = self.env["hr.salary.rule"]

        for payslip in self:
            res = {}
            uom_hour = self.env.ref("product.product_uom_hour")

            if payslip.state != "draft":
                raise UserError(
                    _("Cannot import timesheet activity on non-draft payslip"))

            criteria = [
                ("payslip_id", "=", payslip.id),
                ("import_from_activity", "=", True),
            ]

            obj_worked_days.search(criteria).unlink()

            if not payslip.employee_id.user_id:
                continue

            user = payslip.employee_id.user_id

            if not payslip.contract_id:
                continue

            rule_ids = map(
                lambda x: x[0],
                payslip.contract_id.struct_id.get_all_rules())
            for rule in obj_rule.browse(rule_ids):
                if not rule.timesheet_account_ids:
                    continue

                res = {
                    "name": _("Timesheet activities for %s") % rule.name,
                    "code": "TS.%s" % rule.code,
                    "contract_id": payslip.contract_id.id,
                    "number_of_hours": 0.0,
                    "payslip_id": payslip.id,
                    "import_from_activity": True,
                }

                for account in rule.timesheet_account_ids:
                    criteria = [
                        ("account_id", "child_of", account.id),
                        ("user_id", "=", user.id),
                        ("sheet_id.state", "=", "done"),
                        ("date", ">=", payslip.date_from),
                        ("date", "<=", payslip.date_to),
                    ]
                    for ts_line in obj_timesheet_line.search(
                            criteria):
                        ts_line_hour = obj_uom._compute_qty(
                            ts_line.product_uom_id.id,
                            ts_line.unit_amount,
                            uom_hour.id
                        )
                        res["number_of_hours"] += ts_line_hour
                obj_worked_days.create(res)
