# -*- coding: utf-8 -*-
from odoo import api, fields, models
from cStringIO import StringIO
import xlsxwriter


class ExcelAccountingReport(models.TransientModel):

    _inherit = "accounting.report"

    @api.multi
    def print_excel_report(self):
        self.ensure_one()
        filename = self.account_report_id.name + '.xlsx'
        return {
            'type': 'ir.actions.act_url',
            'url': '/account_report_excel/print?filename=' + filename  + '&model_name=accounting.report&model_curr_id=' + str(self.id),
            'target': 'new',
        }

    @api.multi
    def create_excel_data(self,**kwargs):
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_from', 'date_to', 'journal_ids', 'target_move'])[0]
        used_context = {}
        used_context['journal_ids'] = 'journal_ids' in data['form'] and data['form']['journal_ids'] or False
        used_context['state'] = 'target_move' in data['form'] and data['form']['target_move'] or ''
        used_context['date_from'] = data['form']['date_from'] or False
        used_context['date_to'] = data['form']['date_to'] or False
        used_context['strict_range'] = True if used_context['date_from'] else False
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang', 'en_US'))
        data['form']['account_report_id'] = self.account_report_id
        data['form']['date_from_cmp'] = self.date_from_cmp
        data['form']['date_to_cmp'] = self.date_to_cmp
        data['form']['journal_ids'] = [x.id for x in self.journal_ids]
        data['form']['filter_cmp'] = self.filter_cmp
        data['form']['target_move'] = self.target_move
        for field in ['account_report_id']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        comparison_context = self._build_comparison_context(data)
        data['form']['comparison_context'] = comparison_context

        data['form']['date_from_cmp'] = self.date_from_cmp
        data['form']['debit_credit'] = self.debit_credit
        data['form']['filter_cmp'] = self.filter_cmp
        data['form']['date_to_cmp'] = self.date_to_cmp
        data['form']['enable_filter'] = self.enable_filter
        data['form']['label_filter'] = self.label_filter
        data['form']['target_move'] = self.target_move
        data['form']['account_report_id'] = [x.id for x in self.account_report_id]


        acc_lines = self.env['report.account.report_financial'].get_account_lines(data['form'])
        # target = open('C:\log.txt', 'a')
        # target.write("create_excel_data:acc_lines" + str(self.env.context) + "\n")
        # target.close()

        file_data = StringIO()
        workbook = xlsxwriter.Workbook(file_data)
        format1 = workbook.add_format()
        format1.set_bold()
        format1.set_font_size(30)
        format2 = workbook.add_format()
        format2.set_bold()
        format4 = workbook.add_format()
        format4.set_num_format('#,##0.00')
        worksheet = workbook.add_worksheet()
        if 'lang' in self.env.context and self.env.context.get('lang') == 'ar_SY':
            worksheet.right_to_left()
        worksheet.write(0, 0, fields.Datetime.now())
        worksheet.write(2, 0, self.account_report_id.name, format1)
        if 'lang' in self.env.context and self.env.context.get('lang') == 'ar_SY':
            worksheet.write(4, 0, 'الحركات المستهدفة', format2)
        else:
            worksheet.write(4, 0, 'Target Moves', format2)
        worksheet.write(5, 0, dict(self.fields_get(allfields=['target_move'])['target_move']['selection'])[self.target_move])

        if len(acc_lines):
            if 'lang' in self.env.context and self.env.context.get('lang') == 'ar_SY':
                worksheet.write(7, 0, 'الحساب', format2)
                if 'debit' in acc_lines[0]:
                    worksheet.write(7, 1, 'مدين', format2)
                    worksheet.write(7, 2, 'دائن', format2)
                    worksheet.write(7, 3, 'الرصيد', format2)
                elif 'balance_cmp' in acc_lines[0]:
                    worksheet.write(7, 1, 'الرصيد', format2)
                    worksheet.write(7, 2, data['form']['label_filter'], format2)
                else:
                    worksheet.write(7, 1, 'الرصيد', format2)
            else:
                worksheet.write(7, 0, 'Name', format2)
                if 'debit' in acc_lines[0]:
                    worksheet.write(7, 1, 'Debit', format2)
                    worksheet.write(7, 2, 'Credit', format2)
                    worksheet.write(7, 3, 'Balance', format2)
                elif 'balance_cmp' in acc_lines[0]:
                    worksheet.write(7, 1, 'Balance', format2)
                    worksheet.write(7, 2, data['form']['label_filter'], format2)
                else:
                    worksheet.write(7, 1, 'Balance', format2)
            row=8
            for line in acc_lines:
                if line['level'] == 0:
                    continue
                format3 = workbook.add_format()
                format3.set_indent(line['level'])
                worksheet.write(row,0,line['name'],format3)
                if 'debit' in line:
                    worksheet.write(row, 1, line['debit'],format4)
                    worksheet.write(row, 2, line['credit'],format4)
                    worksheet.write(row, 3, line['balance'],format4)
                elif 'balance_cmp' in line:
                    worksheet.write(row, 1, line['balance'],format4)
                    worksheet.write(row, 2, line['balance_cmp'],format4)
                else:
                    worksheet.write(row, 1, line['balance'],format4)
                row +=1
        workbook.close()
        file_data.seek(0)
        file_content = file_data.read()
        file_data.close()

        return file_content

