# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2015 Salton Massally (<smassally@idtlabs.sl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import xlwt
from datetime import datetime
from openerp.report import report_sxw
from openerp.addons.report_xls.report_xls import report_xls
from openerp.tools.translate import _
import logging
_logger = logging.getLogger(__name__)


class PayslipRunReportXlsParser(report_sxw.rml_parse):

    def __init__(self, cursor, uid, name, context):
        super(PayslipRunReportXlsParser, self).__init__(
            cursor, uid, name, context=context)

        company = self.pool.get('res.users').browse(
            self.cr, uid, uid, context=context).company_id
        header_report_name = ' - '.join((_('Payroll Register'),
                                        company.name))

        footer_date_time = self.formatLang(
            str(datetime.today()), date_time=True)

        self.localcontext.update({
            'cr': self.cr,
            'uid': self.uid,
            'report_name': _('Payroll Register'),
            'additional_args': [
                ('--header-font-name', 'Helvetica'),
                ('--footer-font-name', 'Helvetica'),
                ('--header-font-size', '10'),
                ('--footer-font-size', '6'),
                ('--header-left', header_report_name),
                ('--header-spacing', '2'),
                ('--footer-left', footer_date_time),
                ('--footer-right',
                 ' '.join((_('Page'), '[page]', _('of'), '[topage]'))),
                ('--footer-line',),
            ],
        })

    def set_context(self, objects, data, ids, report_type=None):
        start_date = data['date_start']
        stop_date = data['date_end']
        run_name = data['run_name']
        run_lines = {}
        run_totals = {}

        for slip in objects:
            slip_data = {}
            for line in slip.line_ids:
                slip_data[line.salary_rule_id.code] = line.total
                if line.salary_rule_id.code not in run_totals:
                    run_totals[line.salary_rule_id.code] = line.total
                else:
                    run_totals[line.salary_rule_id.code] += line.total
            run_lines[slip.id] = slip_data

        self.localcontext.update({
            'start_date': start_date,
            'stop_date': stop_date,
            'run_name': run_name,
            'run_lines': run_lines,
            'run_totals': run_totals
        })

        return super(PayslipRunReportXlsParser, self).set_context(
            objects, data, ids, report_type=report_type)


class PayslipRunReportXls(report_xls):
    column_sizes = [12, 12, 20, 15, 30, 30, 14, 14, 14, 14, 14, 14, 10]

    def _get_columns(self):
        '''
        returns the number of columns
        '''
        self._report_info_columns = [
            ('display_name', 'Name', 25),
            ('identification_id', 'ID #', 10),
            ('bank_account_id', 'Bank Account', 20),
            ('department_id', 'Department', 30),
        ]
        self._report_pay_slip_columns = []
        user = self.pool['res.users'].browse(self.cr, self.uid, self.uid)
        rule_ids = self.pool['hr.salary.rule'].search(
            self.cr,
            self.uid,
            [
                ('company_id', '=', user.company_id.id),
                ('appears_on_payslip', '=', True)
            ],
            order="sequence"
        )
        rule_obj = self.pool['hr.salary.rule']
        for rule in rule_obj.browse(self.cr, self.uid, rule_ids):
            self._report_pay_slip_columns.append(
                (rule.code, rule.name, len(rule.name))
            )
        self._report_columns = self._report_info_columns \
            + self._report_pay_slip_columns

    def global_initializations(self, wb, _p, xlwt, _xs, objects, data):
        # this procedure will initialise variables and Excel cell styles and
        # return them as global ones
        self.ws = wb.add_sheet(_p.report_name[:31])
        self.ws.panes_frozen = True
        self.ws.remove_splits = True
        self.ws.portrait = 0  # Landscape
        self.ws.fit_width_to_pages = 1
        self.ws.header_str = self.xls_headers['standard']
        self.ws.footer_str = self.xls_footers['standard']

        # initialize columns
        self._get_columns()
        # number of columns
        self.nbr_columns = len(self._report_columns)
        # -------------------------------------------------------
        # cell style for report title
        self.style_font12 = xlwt.easyxf(_xs['xls_title'])
        # -------------------------------------------------------
        self.style_default = xlwt.easyxf(_xs['borders_all'])
        # -------------------------------------------------------
        self.style_default_italic = xlwt.easyxf(
            _xs['borders_all'] + _xs['italic'])
        # -------------------------------------------------------
        self.style_bold = xlwt.easyxf(_xs['bold'] + _xs['borders_all'])
        # -------------------------------------------------------
        self.style_bold_blue_center = xlwt.easyxf(
            _xs['bold'] + _xs['fill_blue'] + _xs['borders_all'] +
            _xs['center'])
        # -------------------------------------------------------
        self.style_center = xlwt.easyxf(
            _xs['borders_all'] + _xs['wrap'] + _xs['center'])
        # -------------------------------------------------------
        self.style_yellow_bold = xlwt.easyxf(
            _xs['bold'] + _xs['fill'] + _xs['borders_all'])
        self.style_yellow_bold_decimal = xlwt.easyxf(
            _xs['bold'] + _xs['fill'] + _xs['borders_all'],
            num_format_str=report_xls.decimal_format)
        # -------------------------------------------------------
        self.style_yellow_bold_right = xlwt.easyxf(
            _xs['bold'] + _xs['fill'] + _xs['borders_all'] + _xs['right'])
        # -------------------------------------------------------
        self.style_right = xlwt.easyxf(_xs['borders_all'] + _xs['right'])
        # -------------------------------------------------------
        self.style_right_italic = xlwt.easyxf(
            _xs['borders_all'] + _xs['right'] + _xs['italic'])
        # -------------------------------------------------------
        self.style_decimal = xlwt.easyxf(
            _xs['borders_all'] + _xs['right'],
            num_format_str=report_xls.decimal_format)
        # -------------------------------------------------------
        self.style_decimal_italic = xlwt.easyxf(
            _xs['borders_all'] + _xs['right'] + _xs['italic'],
            num_format_str=report_xls.decimal_format)
        # -------------------------------------------------------
        self.style_date = xlwt.easyxf(
            _xs['borders_all'] + _xs['left'],
            num_format_str=report_xls.date_format)
        # -------------------------------------------------------
        self.style_date_italic = xlwt.easyxf(
            _xs['borders_all'] + _xs['left'] + _xs['italic'],
            num_format_str=report_xls.date_format)

    def print_title(self, _p, row_position):
        period_str = '%s to %s' % (_p.start_date, _p.stop_date)
        report_name = ' - '.join([_p.report_name.upper(),
                                  _p.company.partner_id.name,
                                  period_str])
        c_specs = [('report_name', self.nbr_columns, 0, 'text', report_name), ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(
            self.ws, row_position, row_data, row_style=self.style_font12)
        return row_position

    # send an empty row to the Excel document
    def print_empty_row(self, row_position):
        c_sizes = self.column_sizes
        c_specs = [('empty%s' % i, 1, c_sizes[i], 'text', None)
                   for i in range(0, len(c_sizes))]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(
            self.ws, row_position, row_data, set_column_size=True)
        return row_position

    # Fill in the titles of the header summary tables: Chart of account -
    # Fiscal year - ...
    def print_header_titles(self, _p, data, row_position):
        c_specs = []
        column_index = 0
        for column in self._report_columns:
            c_specs.append(
                (
                    column[0].lower(),
                    1,
                    0,
                    'text',
                    column[1].upper(),
                    None,
                    self.style_bold_blue_center
                ),
            )
            cwidth = self.ws.col(column_index).width
            if ((column[2] * 367)) > cwidth:
                # (Modify column width to match biggest data in that column)
                self.ws.col(column_index).width = (column[2] * 367)
            column_index += 1
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(
            self.ws, row_position, row_data,
            row_style=self.style_bold_blue_center)
        return row_position

    def print_run_lines(self, row_position, slip, _xs, xlwt, _p, data):
        employee = slip.employee_id
        slip_data = _p['run_lines'][slip.id]
        read_cols = [column[0] for column in self._report_info_columns]
        info_data = self.pool['hr.employee'].read(
            self.cr, self.uid, employee.id, read_cols)

        c_specs = []
        for column in self._report_info_columns:
            value = info_data[column[0]]
            if isinstance(value, tuple):
                value = value[1]
            c_specs.append(
                (
                    column[0].lower(),
                    1,
                    0,
                    'text',
                    value,
                    None,
                ),
            )

        for column in self._report_pay_slip_columns:
            value = column[0] in slip_data and slip_data[column[0]] or 0
            c_specs.append(
                (
                    column[0].lower(),
                    1,
                    0,
                    'number',
                    value,
                    None,
                    self.style_decimal
                ),
            )
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(
            self.ws, row_position, row_data)
        return row_position

    def print_totals(self, _p, data, row_position):
        totals = _p['run_totals']
        c_specs = []
        for column in self._report_info_columns:
            c_specs.append(
                (
                    column[0].lower(),
                    1,
                    0,
                    'text',
                    '',
                    None,
                ),
            )

        for column in self._report_pay_slip_columns:
            value = column[0] in totals and totals[column[0]] or 0
            c_specs.append(
                (
                    column[0].lower(),
                    1,
                    0,
                    'number',
                    value,
                    None,
                ),
            )
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(
            self.ws, row_position, row_data,
            row_style=self.style_yellow_bold_decimal)
        return row_position

    def generate_xls_report(self, _p, _xs, data, objects, wb):  # main function

        # Initializations
        self.global_initializations(wb, _p, xlwt, _xs, objects, data)
        row_pos = 0
        # Print Title
        row_pos = self.print_title(_p, row_pos)
        # Print empty row to define column sizes
        row_pos = self.print_empty_row(row_pos)
        # Print Header Table titles
        row_pos = self.print_header_titles(_p, data, row_pos)
        # Freeze the line
        self.ws.set_horz_split_pos(row_pos)

        for slip in objects:
            # let's print data"
            row_pos = self.print_run_lines(
                row_pos, slip, _xs, xlwt, _p, data)

        # Print totals
        row_pos = self.print_totals(_p, data, row_pos)

PayslipRunReportXls(
    'report.payroll.run_xls',
    'hr.payslip',
    parser=PayslipRunReportXlsParser
)
