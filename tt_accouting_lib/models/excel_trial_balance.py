# -*- coding: utf-8 -*-
from odoo import api, fields, models
from cStringIO import StringIO
import xlsxwriter


class ExcelTrialBalReport(models.TransientModel):

    _inherit = "account.balance.report"

    @api.multi
    def print_excel_report(self):
        self.ensure_one()
        filename = 'Trial_Balance.xlsx'
        if 'lang' in self.env.context and self.env.context.get('lang') == 'ar_SY':
            filename = 'ميزان المراجعة.xlsx'
        else:
            filename = 'Trial_Balance.xlsx'
        act_ids = ''
        act_mod_name=''
        if 'active_model' in self.env.context:
            act_mod_name = self.env.context.get('active_model')
            for x in self.env.context.get('active_ids'):
                act_ids = act_ids+ str(x) + ','
        return {
            'type': 'ir.actions.act_url',
            'url': '/account_report_excel/print?filename=' + filename + '&model_name=account.balance.report&model_curr_id=' + str(
                self.id) + '&act_mod_name=' + str(act_mod_name) + '&act_ids=' + act_ids,
            'target': 'new',
        }

    @api.multi
    def create_excel_data(self,**kwargs):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_from', 'date_to', 'journal_ids', 'target_move'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang', 'en_US'))
        data = self.pre_print_report(data)
        display_account = data['form'].get('display_account')

        if kwargs['act_mod_name'] == 'account.account':
            acccs = []
            for acc_id in kwargs['act_ids'].split(','):
                if acc_id != '':
                    acccs.append(int(acc_id))
            accounts = self.env['account.account'].search([('id','in',acccs)])
        else:
            accounts =self.env['account.account'].search([])
        account_res = self.env['report.account.report_trialbalance'].with_context(data['form'].get('used_context'))._get_accounts(accounts, display_account)
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
            worksheet.write(2, 0, 'ميزان المراجعة', format1)

            worksheet.write(4, 0, 'عرض الحسابات', format2)
            worksheet.write(5, 0, dict(self.fields_get(allfields=['display_account'])['display_account']['selection'])[self.display_account])
            worksheet.write(4, 3, 'الحركات المستهدفة', format2)
            worksheet.write(5, 3, dict(self.fields_get(allfields=['target_move'])['target_move']['selection'])[self.target_move])

            worksheet.write(7, 0, 'الكود', format2)
            worksheet.write(7, 1, 'الحساب', format2)
            worksheet.write(7, 2, 'مدين', format2)
            worksheet.write(7, 3, 'دائن', format2)
            worksheet.write(7, 4, 'الرصيد', format2)
        else:
            worksheet.write(0, 0, fields.Datetime.now())
            worksheet.write(2, 0, 'Trial Balance', format1)

            worksheet.write(4, 0, 'Display Accounts', format2)
            worksheet.write(5, 0, dict(self.fields_get(allfields=['display_account'])['display_account']['selection'])[
                self.display_account])
            worksheet.write(4, 3, 'Target Moves', format2)
            worksheet.write(5, 3, dict(self.fields_get(allfields=['target_move'])['target_move']['selection'])[
                self.target_move])

            worksheet.write(7, 0, 'Code', format2)
            worksheet.write(7, 1, 'Account', format2)
            worksheet.write(7, 2, 'Debit', format2)
            worksheet.write(7, 3, 'Credit', format2)
            worksheet.write(7, 4, 'Balance', format2)

        row = 8
        for line in account_res:
            worksheet.write(row, 0, line['code'])
            worksheet.write(row, 1, line['name'])
            worksheet.write(row, 2, line['debit'],format4)
            worksheet.write(row, 3, line['credit'],format4)
            worksheet.write(row, 4, line['balance'],format4)
            row+=1

        workbook.close()
        file_data.seek(0)
        file_content = file_data.read()
        file_data.close()

        return file_content


