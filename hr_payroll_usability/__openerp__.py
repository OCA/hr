# -*- coding: utf-8 -*-
{
    "name" : "Payroll Usability",
    "version" : "0.1",
    'author': "Salton Massally <smassally@idtlabs.sl>, "
               "Odoo Community Association (OCA)",
    "website" : "http://idtlabs.sl",
    "category" : "Human Resources",
    "summary": "Usability improvements for payroll",
    "depends" : [
        'hr_payroll'
    ],
    "data" : [
        'views/hr_payroll.xml',
        'views/res_config.xml',
    ],
    'installable' : True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
