# -*- coding: utf-8 -*-
#   Copyright (C) 2018 EBII (https://www.saaslys.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api


class HrContract(models.Model):
    _inherit = 'hr.contract'

    amendment_ids = fields.One2many(
        comodel_name='hr.contract.amendment', inverse_name="contract_id",
        string="contract", required=False)

    def _prepare_contract_amendment(self, vals):
        self.ensure_one()
        # find a name
        if 'job_id' in vals.keys() and len(vals) == 1:
            type = 'JOB_CHANGE'
        elif 'wage' in vals.keys() and len(vals) == 1:
            type = 'SALARY_CHANGE'
        elif 'working_hours' in vals.keys() and len(vals) == 1:
            type = 'WORKING_HOURS_CHANGE'
        else:
            type = 'CONTRACT_SITUATION'

        sequence = self.env['ir.sequence'].next_by_code("name")
        return {'contract_id': self.id,
                'name': sequence,
                'amendment_type': type,
                }

    def _save_amemdment_changes(self, vals, amendment):
        self.ensure_one()
        # retreive value name in ir.model.fields
        for k, v in vals.iteritems():
            # if k not in EXCLUDED_FIELDS:
            method = getattr(self, k)
            model_field = self.env['ir.model.fields'].search(
                [('model', '=', 'hr.contract'), ('name', '=', k)])

            save = True
            if model_field.ttype == 'many2one':
                new = self.env[model_field.relation].browse(v)
                value_new = new.name
                value_before = method.name
                if value_new == value_before:
                    save = False

            if model_field.ttype == 'many2many':
                # import pdb; pdb.set_trace()
                old_ids = method.ids
                list_ids = list(v[0][2])
                print "old %s / new %s " % (old_ids, list_ids)
                remove_ids = [x for x in old_ids if x not in list_ids]
                add_ids = [x for x in list_ids if x not in old_ids]
                if len(remove_ids) > 0:
                    for m2m_id in remove_ids:
                        new = self.env[model_field.relation].browse(m2m_id)
                        value_new = "remove"
                        value_before = new.name
                        if value_new != value_before:
                            amendmentChangesVals = {
                                'amendment': amendment.id,
                                'value_name': model_field.display_name,
                                'value_before': value_before,
                                'value_new': value_new,
                            }
                            self.env[
                                'hr.contract.amendment.changes'].create(
                                amendmentChangesVals)
                if len(add_ids) > 0:
                    for m2m_id in add_ids:
                        new = self.env[model_field.relation].browse(
                            m2m_id)
                        value_new = new.name
                        value_before = ""
                        if value_new != value_before:
                            amendmentChangesVals = {
                                'amendment': amendment.id,
                                'value_name': model_field.display_name,
                                'value_before': value_before,
                                'value_new': value_new,
                            }
                            self.env[
                                'hr.contract.amendment.changes'].create(
                                amendmentChangesVals)
                    # save = False
            else:
                value_before = method
                value_new = v
                if value_before != value_new:
                    amendmentChangesVals = {
                        'amendment': amendment.id,
                        'value_name': model_field.display_name,
                        'value_before': value_before,
                        'value_new': value_new,
                    }
                self.env['hr.contract.amendment.changes'].create(
                    amendmentChangesVals)

    @api.multi
    def write(self, vals):

        EXCLUDED_FIELDS = ['notes']
        # don't save notes if it's the only one changes
        if EXCLUDED_FIELDS[0] in vals.keys() and len(vals) == 1:
            return super(HrContract, self).write(vals)
        else:

            for res in self:
                amendmentVals = res._prepare_contract_amendment(vals)
                amendment = res.env[
                    'hr.contract.amendment'].create(amendmentVals)
                res._save_amemdment_changes(vals, amendment)

        return super(HrContract, self).write(vals)
