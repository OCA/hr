# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import wizard
import pooler
import tools
import time
import datetime
import mx.DateTime
import re

mail_form='''<?xml version="1.0"?>
<form string="Interview Mail">
    <field name="smtp_server" colspan="4"/>
    <field name="subject" colspan="4"/>
    <field name="mail_body" colspan="4"/>
</form>'''

mail_fields = {
    'smtp_server':{'string':'SMTP Server','type':'many2one','relation': 'email.smtpclient','required':True},
    'subject': {'string': 'Subject', 'type':'char', 'size': 64, 'required':True},
    'mail_body': {'string': 'Body', 'type': 'text_tag', 'required':True}
}

class wizard_email_interview(wizard.interface):
    
    def merge_message(self, cr, uid, id, keystr, context):
        obj_pool = pooler.get_pool(cr.dbname).get('hr.interview')
        
        def merge(match):
            obj = obj_pool.browse(cr, uid, id)
            exp = str(match.group()[2:-2]).strip()
            result = eval(exp, {'object':obj, 'context': context,'time':time})
            if result in (None, False):
                return str("--------")
            print 'XXXXXXXXXXXXXXXXXXXX : ', result
            return str(result)

        com = re.compile('(\[\[.+?\]\])')
        message = com.sub(merge, keystr)
        
        return message

    def _send_mail(self, cr, uid, data, context={}):
        smtp_obj = pooler.get_pool(cr.dbname).get('email.smtpclient')
        subject = data['form']['subject']
        body = data['form']['mail_body']
        ids = data['ids']
        hr_candidate_obj = pooler.get_pool(cr.dbname).get('hr.interview')
        hr_candidates = hr_candidate_obj.browse(cr,uid,ids)
        for hr_candidate in hr_candidates:
            msg = self.merge_message(cr, uid, hr_candidate.id, body, context)
            to = hr_candidate.email
            files = smtp_obj.send_email(cr, uid, data['form']['smtp_server'], to, subject, msg)
        return {}     

    def _default_params(self, cr, uid, data, context={}):
        ids = data['ids']
        hr_candidates = pooler.get_pool(cr.dbname).get('hr.interview').browse(cr,uid,ids)
        subject = '<No Subject>'
        for hr_candidate in hr_candidates:
            body = "Hello __candidate__ ,\n\n" + "Congratulations!\n\n"
            if hr_candidate.state == 'scheduled':
                body = body + "Your resume has been short listed in the qualifying candidates.\n"\
                            + "Your interview has been scheduled on __date__\n\n"
                subject = "A call for Interview !"
            elif hr_candidate.state == 'selected':
                body = body + "You have been selected .\n"\
                            + "Your date of joining is :  __date__\n\n"
                subject = "Congratulations! A call for Joining!"           
                
        data['mail_body'] = body + "Regards,\n" + "Management\n"
        data['subject'] = subject           
        return data
        
    states = {
        'init': {
            'actions': [_default_params],
            'result': {'type':'form', 'arch':mail_form, 'fields':mail_fields, 'state':[('end','Cancel'),('sendmail','Send Mail')]}
        },
        'sendmail': {
            'actions': [_send_mail],
            'result': {'type':'state', 'state':'end'}
        }
    }
wizard_email_interview('hr.email.interview')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
