# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, _, exceptions
from datetime import datetime, timedelta


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    @api.multi
    def button_import_attendance(self):
        for payslip in self:
            self._import_attendance(payslip)

    @api.model
    def _import_attendance(self, payslip):
        wd_obj = self.env["hr.payslip.worked_days"]
        day_obj = self.env["hr_timesheet_sheet.sheet.day"]
        date_from = payslip.date_from
        date_to = payslip.date_to

        criteria1 = [
            ("payslip_id", "=", payslip.id),
            ("import_from_attendance", "=", True),
        ]
        wd_obj.search(criteria1).unlink()

        res = {
            "name": _("Total Attendance"),
            "code": "ATTN",
            "number_of_days": 0.0,
            "number_of_hours": 0.0,
            "contract_id": payslip.contract_id.id,
            "import_from_attendance": True,
            "payslip_id": payslip.id,
        }

        criteria2 = [
            ("sheet_id.date_from", ">=", date_from),
            ("sheet_id.date_to", "<=", date_to),
            ("sheet_id.employee_id", "=", payslip.employee_id.id),
        ]

        for day in day_obj.search(criteria2):
            if day.total_attendance >= 0.0:
                res["number_of_days"] += 1
                res["number_of_hours"] += day.total_attendance

        wd_obj.create(res)

    @api.model
    def get_worked_day_lines(self, contract_ids, 
            date_from, date_to):
        def was_on_leave(employee_id, datetime_day):
            res = False
            day = datetime_day.strftime("%Y-%m-%d")
            obj_holiday = self.env["hr.holidays"]
            holidays = obj_holiday.search([
                ("state","=","validate"),
                ("employee_id","=",employee_id),
                ("type","=","remove"),
                ("date_from","<=",day),
                ("date_to",">=",day)])
            if holidays:
                res = holidays[0].holiday_status_id.name
            return res

        res = []
        obj_contract = self.env["hr.contract"]
        for contract in obj_contract.browse(contract_ids):
            # raise exceptions.Warning("c")
            if not contract.working_hours:
                #fill only if the contract as a working schedule linked
                continue
            attendances = {
                 'name': _("Normal Working Days paid at 100%"),
                 'sequence': 1,
                 'code': 'WORK100',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,
            }
            leaves = {}
            day_from = datetime.strptime(date_from,"%Y-%m-%d")
            day_to = datetime.strptime(date_to,"%Y-%m-%d")
            nb_of_days = (day_to - day_from).days + 1
            obj_calendar = self.env["resource.calendar"]
            for day in range(0, nb_of_days):
                working_hours_on_day = obj_calendar.working_hours_on_day(
                        contract.working_hours, 
                        day_from + timedelta(days=day))
                if working_hours_on_day:
                    #the employee had to work
                    leave_type = was_on_leave(
                            contract.employee_id.id, 
                            day_from + timedelta(days=day))
                    if leave_type:
                        #if he was on leave, fill the leaves dict
                        if leave_type in leaves:
                            leaves[leave_type]['number_of_days'] += 1.0
                            leaves[leave_type]['number_of_hours'] += working_hours_on_day
                        else:
                            leaves[leave_type] = {
                                'name': leave_type,
                                'sequence': 5,
                                'code': leave_type,
                                'number_of_days': 1.0,
                                'number_of_hours': working_hours_on_day,
                                'contract_id': contract.id,
                            }
                    else:
                        #add the input vals to tmp (increment if existing)
                        obj_day = self.env["hr_timesheet_sheet.sheet.day"]
                        date_attn = (day_from + timedelta(days=day)).strftime("%Y-%m-%d")
                        criteria2 = [
                            ("name", "=", date_attn),
                            ("sheet_id.employee_id", "=", contract.employee_id.id),
                        ]
                        attn = obj_day.search(criteria2)
                        if attn:
                            attendances['number_of_days'] += 1.0
                            attendances['number_of_hours'] += attn[0].total_attendance
            leaves = [value for key,value in leaves.items()]
            res += [attendances] + leaves
        return res
