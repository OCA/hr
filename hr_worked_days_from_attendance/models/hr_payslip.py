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
            obj_ts_day = self.env["hr_timesheet_sheet.sheet.day"]
            obj_attendance = self.env["hr.attendance"]
            for day in range(0, nb_of_days):
                criteria = [
                        ("name", "=", (day_from + timedelta(days=day)).strftime("%Y-%m-%d %H:%M:%S")),
                    ("sheet_id.employee_id.id", "=", contract.employee_id.id),
                    ("sheet_id.state", "=", "done"),
                    ]
                ts_days = obj_ts_day.search(criteria)

                if not ts_days:
                    continue

                ts_day = ts_days[0]
                
                # Continue if sheet day does not has a valid
                # first_attendance_id and last_attendance_id.
                # Line bellow addes because first_attendance_id and
                # last_attendance_id are not stored.
                if not ts_day.first_attendance_id or \
                        not ts_day.last_attendance_id:
                    continue

                criteria2 = [
                    ("attendance_day_id.id", "=", ts_day.id),
                    ("id", ">=", ts_day.first_attendance_id.id),
                    ("id", "<=", ts_day.last_attendance_id.id),
                    ]

                ts_attendances = obj_attendance.search(criteria2)

                if len(ts_attendances) == 0:
                    continue

                #if attendace exist add number_of_days
                attendances['number_of_days'] += 1.0

                for attn_counter in range(0, len(ts_attendances)-1, 2):
                    # working_hours = contract.working_hours.get_working_hours_of_date(
                    #         datetime.strptime(ts_attendances[attn_counter].name, "%Y-%m-%d %H:%M:%S"),
                    #         datetime.strptime(ts_attendances[attn_counter+1].name, "%Y-%m-%d %H:%M:%S"),
                    #         )[0]
                    working_hours = contract.working_hours.get_working_hours_of_date(
                            datetime.strptime("2016-07-01 00:00:00", "%Y-%m-%d %H:%M:%S"),
                            datetime.strptime("2016-07-01 23:59:00", "%Y-%m-%d %H:%M:%S"),
                            )[0]

                    attendances['number_of_hours'] += working_hours

            res += [attendances]
        return res
