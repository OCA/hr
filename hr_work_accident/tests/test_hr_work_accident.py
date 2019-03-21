# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestHrWorkAccident(TransactionCase):

    def test_create_work_accident(self):
        employee = self.env['hr.employee'].create({
            'name': 'Employee',
        })
        accident_type = self.env['hr.work.accident.type'].create({
            'name': 'Accident',
        })
        work_accident = self.env['hr.work.accident'].create({
            'accident_type': accident_type.id,
            'date': '2019-02-02',
            'hours_working': 12,
            'location': 'Office',
            'description': 'BlaBla',
            'causes': 'BlaBla',
            'affected_employees': [(0, 0, {
                'employee_id': employee.id,
                'injury_severity': 'serious',
            })],
            'risks': [(0, 0, {
                'name': 'Working a lot',
                'description': 'Description',
                'probability': 'rare',
                'frequency': 'continuous',
                'consequences': 'important',
                'magnitude': 'high',
            })],
            'actions': [
                (0, 0, {
                    'name': 'Action 1',
                    'description': 'Description',
                    'cost': 25,
                    'employee_ids': [(4, employee.id)],
                    }
                 ),
                (0, 0, {
                    'name': 'Action 2',
                    'description': 'Description',
                    'cost': 40,
                    'employee_ids': [(4, employee.id)],
                    }
                 )
            ],
        })
        self.assertTrue(work_accident)
        self.assertEqual(work_accident.total_cost, 65)
        self.assertEqual(work_accident.day_of_week, 'Saturday')
        self.assertEqual(work_accident.state, 'open')
        work_accident.finish_investigation()
        self.assertEqual(work_accident.state, 'closed')
        work_accident.back_to_open()
        self.assertEqual(work_accident.state, 'open')
