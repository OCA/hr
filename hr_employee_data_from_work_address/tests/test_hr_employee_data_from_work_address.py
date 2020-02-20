# -*- coding: utf-8 -*-
# Copyright 2015 Therp BV <http://therp.nl>
from ..init_hook import pre_init_hook, post_init_hook
from openerp.tests.common import TransactionCase


class TestHrEmployeeDataFromWorkAddress(TransactionCase):
    def setUp(self):
        super(TestHrEmployeeDataFromWorkAddress, self).setUp()
        # create employees with same partner to be corrected by the init hook
        self.partner = self.env['res.partner'].create({
            'name': 'testemployee',
        })
        self.employee1 = self.env['hr.employee'].create({
            'name': 'testemployee1',
            'address_id': self.partner.id,
        })
        self.employee2 = self.env['hr.employee'].create({
            'name': 'testemployee1',
            'address_id': self.partner.id,
        })

    def test_01_hooks(self):
        pre_init_hook(self.env.cr)
        self.assertTrue(
            len(
                self.env['hr.employee'].search([
                    ('address_id', '=', self.partner.id),
                ])
            ) > 1
        )
        post_init_hook(self.env.cr, self.env.registry)
        self.assertFalse(self.env['hr.employee'].search([
            ('address_id', '=', self.partner.id),
        ]))

    def test_02_create_write(self):
        user1 = self.env['res.users'].create({
            'name': 'user1',
            'login': 'user1',
        })
        employee = self.env['hr.employee'].create({
            'name': 'employee',
            'address_id': self.env['res.partner'].create({
                'name': 'partner1',
            }).id,
            'user_id': user1.id,
        })
        # user1's partner_id must be replaced by the employee's work address
        self.assertEqual(user1.partner_id, employee.address_id)
        # if we assign a new user, the same should happen
        user2 = self.env['res.users'].create({
            'name': 'user2',
            'login': 'user2',
        })
        employee.write({'user_id': user2.id})
        self.assertEqual(user2.partner_id, employee.address_id)
        employee.write({'address_id': False})
        employee.write({'user_id': user2.id})
        self.assertEqual(user2.partner_id, employee.address_id)

    def test_03_onchange(self):
        address = self.employee1.address_id
        self.employee1._onchange_company()
        self.assertEqual(address, self.employee1.address_id)
        work_phone = self.employee1.work_phone
        mobile_phone = self.employee1.mobile_phone
        self.employee1._onchange_address()
        self.assertEqual(work_phone, self.employee1.work_phone)
        self.assertEqual(mobile_phone, self.employee1.mobile_phone)
        work_email = self.employee1.work_email
        name = self.employee1.name
        image = self.employee1.image
        self.employee1._onchange_user()
        self.assertEqual(work_email, self.employee1.work_email)
        self.assertEqual(name, self.employee1.name)
        self.assertEqual(image, self.employee1.image)
