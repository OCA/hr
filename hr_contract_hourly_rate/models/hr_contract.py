# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Savoir-faire Linux. All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, orm


class hr_contract(orm.Model):
    _inherit = 'hr.contract'
    _columns = {
        'salary_computation_method': fields.selection(
            [
                ('wage', 'Annual Wage'),
                ('hourly_rate', 'Hourly Rate')
            ],
            'Salary Computation Method',
            help="Whether to use the annual wage or an hourly rate "
            "for computation of payslip.",
            required=True,
        ),
    }
    _defaults = {
        'salary_computation_method': 'wage',
    }

    def get_job_hourly_rate(
        self, cr, uid,
        date_from, date_to,
        contract_id,
        job_id=False,
        main_job=False,
        context=None,
    ):
        """
        Get the hourly rate related to a job on a contract for a given
        interval of time (date_from, date_to)

        2 cases: get the hourly rate
         - related to a given job position id (job_id == int)
         - related to the main job on the contract (main_job == True)

        This function is intended to be used on payslip worked days to fill the
        hourly_rate field.

        If no rate completely overlap the given period (date_from, date_to),
        False is returned and the hourly rate must then be entered manually.
        """
        contract = self.browse(cr, uid, contract_id, context=context)

        # This does not apply when employee is paid by wage
        if contract.salary_computation_method == 'wage':
            return False

        for contract_job in contract.contract_job_ids:
            # Check case 1 or case 2
            if (job_id and contract_job.job_id.id == job_id) \
                    or (main_job and contract_job.is_main_job):
                # The contract_job belongs to a salary class
                # The salary class contains rates
                for rate in contract_job.hourly_rate_class_id.line_ids:
                    if(
                        # We need the rate that fits the given dates
                        rate.date_start <= date_from
                        and not rate.date_end or date_to <= rate.date_end
                    ):
                        return rate.rate
                break
        return False

    def _check_has_hourly_rate_class(
        self, cr, uid, ids, context=None,
    ):
        """
        Check if every contract job on the contract has an hourly rate
        class assigned to it.
        """
        for contract in self.browse(cr, uid, ids, context=context):

            # This does not apply when employee is paid by wage
            if contract.salary_computation_method == 'hourly_rate':
                for contract_job in contract.contract_job_ids:
                    if not contract_job.hourly_rate_class_id:
                        return False

            return True

    _constraints = [(
        _check_has_hourly_rate_class,
        "Error! At least one job on contract has no hourly rate "
        "class assigned.",
        ['contract_job_ids']
    )]
