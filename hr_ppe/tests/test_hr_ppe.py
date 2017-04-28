# -*- coding: utf-8 -*-
# Copyright © 2017 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.tests import common
from psycopg2 import IntegrityError


class TestHrPpe(common.TransactionCase):

    def setUp(self):
        super(TestHrPpe, self).setUp()
        self.partner_model = self.env['res.partner']
        self.employee_model = self.env['hr.employee']
        self.job_model = self.env['hr.job']
        self.job = self.job_model.create({'name': 'Job 1'})
        self.partner = self.partner_model.create({
            'name': 'Partner 1',
        })
        self.employee = self.employee_model.create({
            'name': 'Employee 1',
        })
        self.product = self.browse_ref('product.product_product_32')
        self.product.write({'ppe_ok': True})

    def test_ppe_picking_creation(self):
        self.job.write({
            'ppe_ids': [(0, 0, {'product_id': self.product.id,
                                'product_uom_id': self.product.uom_id.id})]
        })
        self.employee.write({
            'job_id': self.job.id,
            'address_home_id': self.partner.id,
        })
        self.assertFalse(self.employee.ppe_picking_ids)
        self.assertEquals(self.employee.count_ppe_pickings, 0)
        self.employee.button_create_ppe_picking()
        self.employee.invalidate_cache()
        self.assertTrue(self.employee.ppe_picking_ids)
        self.assertEquals(self.employee.count_ppe_pickings, 1)

    def test_ppe_picking_creation_open_job(self):
        self.employee.write({
            'job_id': self.job.id,
            'address_home_id': self.partner.id,
        })
        self.assertEquals(self.employee.count_ppe_pickings, 0)
        self.assertFalse(self.employee.job_id.ppe_ids)
        result = self.employee.button_create_ppe_picking()
        action = self.browse_ref('hr.action_hr_job')
        self.assertEquals(result.get('display_name'), action.display_name)
        self.assertEquals(result.get('res_id'), self.job.id)

    def test_ppe_picking_creation_add_partner(self):
        self.job.write({
            'ppe_ids': [(0, 0, {'product_id': self.product.id,
                                'product_uom_id': self.product.uom_id.id})]
        })
        self.employee.write({
            'job_id': self.job.id,
        })
        self.assertEquals(self.employee.count_ppe_pickings, 0)
        self.assertFalse(self.employee.address_home_id)
        result = self.employee.button_create_ppe_picking()
        action = self.browse_ref(
            'hr_ppe.hr_employee_partner_selection_wizard_action')
        self.assertEquals(result.get('display_name'), action.display_name)
        add_partner_wiz = self.env[
            'hr.employee.partner.selection'].with_context(
            active_id=self.employee.id,
            active_model=self.employee._model._name,
            create_ppe_picking=True).create({})
        self.assertEquals(add_partner_wiz.employee_id, self.employee)
        self.assertFalse(add_partner_wiz.partner_id)
        add_partner_wiz.write({'partner_id': self.partner.id})
        add_partner_wiz.button_partner_select()
        self.employee.invalidate_cache()
        self.assertEquals(self.employee.address_home_id, self.partner)
        self.assertEquals(self.employee.count_ppe_pickings, 1)

    def test_ppe_list_sql_constraint(self):
        with self.assertRaises(IntegrityError):
            self.job.write({
                'ppe_ids': [(0, 0, {'product_id': self.product.id,
                                    'product_uom_id': self.product.uom_id.id,
                                    'product_uom_qty': 0.0})]
            })
