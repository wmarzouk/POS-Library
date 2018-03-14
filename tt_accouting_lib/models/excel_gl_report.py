# -*- coding: utf-8 -*-
from odoo import api, fields, models , _
from cStringIO import StringIO
from odoo.exceptions import UserError
import xlsxwriter


class ExcelGlReport(models.TransientModel):

    _inherit = 'account.report.general.ledger'

    @api.multi
    def print_excel_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_from', 'date_to', 'journal_ids', 'target_move'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang', 'en_US'))
        data = self.pre_print_report(data)
        data['form'].update(self.read(['initial_balance', 'sortby'])[0])
        if data['form'].get('initial_balance') and not data['form'].get('date_from'):
            raise UserError(_("You must define a Start Date"))
        filename = 'General_Ledger.xlsx'
        if 'lang' in self.env.context and self.env.context.get('lang') == 'ar_SY':
            filename = 'الأستاذ العام.xlsx'
        else:
            filename = 'General_Ledger.xlsx'
        act_ids = ''
        act_mod_name = ''
        if 'active_model' in self.env.context:
            act_mod_name = self.env.context.get('active_model')
            for x in self.env.context.get('active_ids'):
                act_ids = act_ids + str(x) + ','
        return {
            'type': 'ir.actions.act_url',
            'url': '/account_report_excel/print?filename=' + filename + '&model_name=account.report.general.ledger&model_curr_id=' + str(
                self.id) + '&act_mod_name=' + str(act_mod_name) + '&act_ids=' + act_ids,
            'target': 'new',
        }

    @api.multi
    def create_excel_data(self, **kwargs):
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_from', 'date_to', 'journal_ids', 'target_move'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang', 'en_US'))
        data = self.pre_print_report(data)
        data['form'].update(self.read(['initial_balance', 'sortby'])[0])
        if data['form'].get('initial_balance') and not data['form'].get('date_from'):
            raise UserError(_("You must define a Start Date"))
        self.model = self.env.context.get('active_model')
        init_balance = data['form'].get('initial_balance', True)
        sortby = data['form'].get('sortby', 'sort_date')
        display_account = data['form']['display_account']
        codes = []
        if data['form'].get('journal_ids', False):
            codes = [journal.code for journal in
                     self.env['account.journal'].search([('id', 'in', data['form']['journal_ids'])])]
        if kwargs['act_mod_name'] == 'account.account':
            acccs = []
            for acc_id in kwargs['act_ids'].split(','):
                if acc_id != '':
                    acccs.append(int(acc_id))
            accounts = self.env['account.account'].search([('id','in',acccs)])
        else:
            accounts =self.env['account.account'].search([])
        accounts_res = self.env['report.account.report_generalledger'].with_context(data['form'].get('used_context', {}))._get_account_move_entry(accounts,
                                                                                                       init_balance,
                                                                                                       sortby,
                                                                                                       display_account)
        code_txt = ''
        for c in codes:
            code_txt = code_txt + c + ','
        code_txt = code_txt[:-1]
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
            worksheet.write(2, 0, 'الأستاذ العام', format1)
            worksheet.write(4, 0, 'الیومیات', format2)
            worksheet.write(5, 0, code_txt , format2)
            worksheet.write(4, 3, 'عرض الحسابات', format2)
            worksheet.write(5, 3, dict(self.fields_get(allfields=['display_account'])['display_account']['selection'])[self.display_account])
            worksheet.write(4, 6, 'الحركات المستهدفة', format2)
            worksheet.write(5, 6, dict(self.fields_get(allfields=['target_move'])['target_move']['selection'])[self.target_move])
            worksheet.write(6, 0, 'ترتیب حسب', format2)
            worksheet.write(7, 0, dict(self.fields_get(allfields=['sortby'])['sortby']['selection'])[self.sortby])

            worksheet.write(9, 0, 'التاریخ', format2)
            worksheet.write(9, 1, 'الیومیة', format2)
            worksheet.write(9, 2, 'عمبل مورد', format2)
            worksheet.write(9, 3, 'الإشارة', format2)
            worksheet.write(9, 4, 'نقل', format2)
            worksheet.write(9, 5, 'تسمیة القید', format2)
            worksheet.write(9, 6, 'المدین', format2)
            worksheet.write(9, 7, 'الدائن', format2)
            worksheet.write(9, 8, 'الرصید', format2)
        else:
            worksheet.write(0, 0, fields.Datetime.now())
            worksheet.write(2, 0, 'General Ledger', format1)
            worksheet.write(4, 0, 'Journals', format2)
            worksheet.write(5, 0, code_txt)
            worksheet.write(4, 3, 'Display Accounts', format2)
            worksheet.write(5, 3, dict(self.fields_get(allfields=['display_account'])['display_account']['selection'])[self.display_account])
            worksheet.write(4, 6, 'Target Moves', format2)
            worksheet.write(5, 6, dict(self.fields_get(allfields=['target_move'])['target_move']['selection'])[self.target_move])
            worksheet.write(6, 0, 'Sorted by', format2)
            worksheet.write(7, 0, dict(self.fields_get(allfields=['sortby'])['sortby']['selection'])[self.sortby])

            worksheet.write(9, 0, 'Date', format2)
            worksheet.write(9, 1, 'JRNL', format2)
            worksheet.write(9, 2, 'Partner', format2)
            worksheet.write(9, 3, 'Ref', format2)
            worksheet.write(9, 4, 'Move', format2)
            worksheet.write(9, 5, 'Entry Label', format2)
            worksheet.write(9, 6, 'Debit', format2)
            worksheet.write(9, 7, 'Credit', format2)
            worksheet.write(9, 8, 'Balance', format2)

        row_counter = 10
        for x in accounts_res:
            acc_name = '    ' + str(x['code']) + ' ' + str(x['name'])
            merge_txt = 'A' + str(row_counter+1) + ":F" + str(row_counter+1)
            worksheet.merge_range(merge_txt, acc_name, format2)
            worksheet.write(row_counter, 6, x['debit'])
            worksheet.write(row_counter, 7, x['credit'])
            worksheet.write(row_counter, 8, x['balance'])
            row_counter += 1
            for line in x['move_lines']:
                worksheet.write(row_counter, 0, line['ldate'])
                worksheet.write(row_counter, 1, line['lcode'])
                worksheet.write(row_counter, 2, line['partner_name'])
                worksheet.write(row_counter, 3, line['lref'])
                worksheet.write(row_counter, 4, line['move_name'])
                worksheet.write(row_counter, 5, line['lname'])
                worksheet.write(row_counter, 6, line['debit'])
                worksheet.write(row_counter, 7, line['credit'])
                worksheet.write(row_counter, 8, line['balance'])
                row_counter += 1
            row_counter += 1
        workbook.close()
        file_data.seek(0)
        file_content = file_data.read()
        file_data.close()
        return file_content

