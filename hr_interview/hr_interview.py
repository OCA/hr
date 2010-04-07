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

from osv import fields,osv
from osv.orm import except_orm
from tools.translate import _
from time import strftime


class candidate_category(osv.osv):
	_name="candidate.category"
	_description="Category Of Candidate"
	_columns={
	    'code':fields.char("Code", size=64, required=True),
		'name' : fields.char("Name", size=64, required=True),
		'question_ids':fields.one2many("category.question","category_id","Question")
		}
candidate_category()


class cateory_question(osv.osv):
	_name="category.question"
	_description="Question Category (Question Belongs to Which Category)"
	_columns={
		'name' :fields.char("Question" ,size=64,required=True),
		'tot_marks':fields.integer("Total Marks",required=True),
		'category_id':fields.many2one("candidate.category","Category")
		}

cateory_question()


class candidate_experience(osv.osv):
	_name="candidate.experience"
	_description="Candidate Experience"
	_columns={
	    'code':fields.char("Code", size=64, required=True),
		'name' : fields.char("Name", size=64, required=True),
		'special':fields.char("Specialization",size =128)
		}
candidate_experience()


class hr_interview(osv.osv):
	_name = "hr.interview"
	_description = "Interview Evaluation"

	def eval_performance(self,cr, uid, ids, *args):
		tech_obj=self.pool.get("technical.skill")
		tot_marks=obt_marks=0
		tech_id=tech_obj.search(cr,uid,[('candidate_id','=',ids[0])])
		if tech_id :
			for rec in tech_obj.browse(cr,uid,tech_id):
				tot_marks += rec.tot_marks
				obt_marks += rec.obt_marks
			self.write(cr, uid, ids, { 'performance' : (obt_marks * 100) / tot_marks })
		return True

	def _constraint_obt_marks(self, cr, uid, ids):
		tech_skill_obj=self.pool.get("technical.skill")
		tech_skill_ids=tech_skill_obj.search(cr,uid,[('candidate_id','=',ids[0])])
		for rec in tech_skill_obj.browse(cr,uid,tech_skill_ids):
			if rec['obt_marks'] > rec['tot_marks'] or rec['tot_marks'] <= 0 :
			    return False
		return True

	def _constraint_evaluator(self, cr, uid, ids):
		rec = self.read(cr,uid,ids[0])
		if rec['reference_id']:
			if rec['reference_id'][0] in rec['evaluator_ids']:
				return False
		return True

	_columns ={
		'hr_id' : fields.char("Interview ID", size =64),
		'name':fields.char("Candidate Name", size=64, required = True,select = True),
		'crm_case_id' : fields.many2one('crm.case',"Case"),
		'email' : fields.char("E-mail",size=64,required =True),
		'mobile_no' :fields.char("Mobile",size=64),
		'date' :fields.datetime('Scheduled Date'),
		'exam_date' :fields.datetime('Exam On'),
		'education': fields.selection([("be_ce","BE Computers"),("be_it","BE IT"),("bsc_it","BSc IT"),("bca","BCA"),("btech_ce","BTech Computers"),("btech_it","BTech IT"),("mca","MCA"),("msc_it","MSc IT"),("mtech_ce","MTech Computers"),("other","Other")],"Education"),
		'category_id' : fields.many2one("candidate.category","Category"),
		'experience_id':fields.many2one("candidate.experience","Experience"),
		'remarks':fields.text("Remarks"),
		'evaluator_ids': fields.many2many("hr.employee",'hr_empl_rel', 'hr_cand_id', 'emp_id',"Evaluator"),
		'reference_id': fields.many2one("hr.employee","Reference"),
		'tech_skills_ids': fields.one2many("technical.skill","candidate_id","Technology Skills"),
		'performance': fields.float("Performance (%)",readonly=True),
		'state' : fields.selection([("draft","Draft"),('scheduled','Scheduled'),('re-scheduled','Re-Scheduled'),('start-interview','Start-Interview'),('end-interview','End-Interview'),("selected","Selected"),('rejected','Rejected'),("cancel","Cancel")],"State",readonly=True,select =1),
		'history_log_ids': fields.one2many("hr.interview.log","history_id","Interview Logs",readonly=True),
	}
	_defaults = {
         'state' : lambda *a: "draft",
		 'hr_id': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'hr.interview'),
	}

	_constraints = [
        (_constraint_obt_marks, _('Obtained marks cannot be greater than Total marks!'), ['obt_marks']),
        (_constraint_evaluator, "Reference Person cannot be among Evaluators!", ['reference_id'])
    ]

	def state_scheduled(self, cr, uid, ids,*arg):
		self.write(cr, uid, ids, { 'state' : 'scheduled'})
		self._log(cr,uid,ids,'scheduled')
		return True

	def state_cancel(self, cr, uid, ids,*arg):
		self.write(cr, uid, ids, { 'state' : 'cancel' })
		self._log(cr,uid,ids,'cancel')
		return True

	def state_re_scheduled(self, cr, uid, ids,*arg):
		self.write(cr, uid, ids, { 'state' : 're-scheduled' })
		self._log(cr,uid,ids,'re-scheduled')
		return True

	def state_start_interview(self, cr, uid, ids,*arg):
		self.write(cr, uid, ids, { 'state' : 'start-interview' })
		self._log(cr,uid,ids,'start-interview')
		return True

	def state_end_interview(self, cr, uid, ids,*arg):
		self.write(cr, uid, ids, { 'state' : 'end-interview' })
		self._log(cr,uid,ids,'end-interview')
		return True

	def state_selected(self, cr, uid, ids,*arg):
		self.write(cr, uid, ids, { 'state' : 'selected' })
		self._log(cr,uid,ids,'selected')
		return True

	def state_rejected(self, cr, uid, ids,*arg):
		self.write(cr, uid, ids, { 'state' : 'rejected' })
		self._log(cr,uid,ids,'rejected')
		return True

	def _log(self,cr,uid,ids,action):
		his_obj = self.pool.get("hr.interview.log")
		his_obj.create(cr,uid,{'state':action,'date':strftime("%Y-%m-%d %H:%M:%S"),"user_id":uid,'history_id':ids[0]})
		return True

	def copy(self, cr, uid, id, default=None,context=None):
		raise osv.except_osv(_('Error !'),_('You cannot duplicate the resource!'))
		return False

	def create(self, cr, uid, vals, context=None):
		que_obj = self.pool.get("category.question")
		tech_skill_obj = self.pool.get("technical.skill")
		hr_id = super(hr_interview, self).create(cr, uid, vals, context=context)
		if vals.get('category_id', False):
			cate_id = vals.get('category_id')
			que_ids = que_obj.search(cr, uid, [('category_id','=',int(cate_id))], context=context)
			for rec in que_obj.browse(cr, uid, que_ids, context=context):
				tech_skill_obj.create(cr, uid, {'name': rec.name, 'tot_marks': rec.tot_marks, 'candidate_id': hr_id})
		self._log(cr, uid, [hr_id], 'draft')
		return hr_id

	def write(self, cr, uid, ids, vals, context=None):
		que_obj = self.pool.get("category.question")
		tech_skill_obj=self.pool.get("technical.skill")
		if 'category_id' in vals :
			cate_id = vals['category_id']
			que_ids = que_obj.search(cr, uid, [('category_id', '=', int(cate_id))])
			tech_skill_ids=tech_skill_obj.search(cr, uid, [('candidate_id','=',ids[0])])
			if tech_skill_ids:
				tech_skill_obj.unlink(cr,uid,tech_skill_ids)
			for rec in que_obj.browse(cr,uid,que_ids):
				tech_skill_obj.create(cr,uid,{'name':rec.name,'tot_marks':rec.tot_marks,'candidate_id':ids[0]})
		return super(hr_interview, self).write(cr, uid, ids, vals, context=context)

hr_interview()


class technical_skill(osv.osv):
	_name="technical.skill"
	_description="Technical Skill Of Candidate"
	_columns={
		'candidate_id' : fields.many2one("hr.interview","Candidate ID"),
		'name' : fields.char("Category" ,size=64),
		'tot_marks' : fields.float("Total Marks"),
		'obt_marks': fields.float("Obtained Marks"),
		'remarks' : fields.text("Remarks")
		}
technical_skill()


class hr_interview_log(osv.osv):
	_name="hr.interview.log"
	_description="HR interview log"
	_rec_name="history_id"
	_columns={
		'history_id':fields.many2one("hr.interview","History ID"),
		'state' : fields.char("State",size=64),
		'date': fields.datetime("Date"),
		'user_id' : fields.many2one("res.users","User Name")
		}
hr_interview_log()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
