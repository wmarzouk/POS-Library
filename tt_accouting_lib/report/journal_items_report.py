from odoo import api, models
from datetime import date, datetime, time, timedelta
from dateutil.relativedelta import relativedelta
from itertools import groupby,islice
import collections



class ParticularReport(models.AbstractModel):
    _name = 'report.tt_journal_report.report_financial_position'


    def _get_sum_credit(self,list_items=[]):
        credit = 0.0
        for l in list_items:
            credit += l.credit
        return credit

    def _get_sum_debit(self, list_items=[]):
        debit = 0.0
        for l in list_items:
            debit += l.debit
        return debit

    def _get_items(self,list_items=[]):
        acc_list=[]
        items=[]
        acc_r=[]
        data=[]
        analytic=''
        acc_name=''
        for line in list_items:

            items.append(line.account_id.id)

            if line.account_id.id not in acc_list:
                acc_list.append(line.account_id.id)
            else:
                acc_r.append(line.account_id.id)

        acc_r = list(set(acc_r))
        for l in list_items:
            if l.analytic_account_id:
                analytic = l.analytic_account_id.name
            if l.account_id.id in acc_r:
                analytic = ''
                continue

            else:
                result = {
                    'acc_analytic': analytic,
                    'debit': l.debit,
                    'credit': l.credit,
                    'acc_name': l.account_id.name,
                    'acc_code': l.account_id.code,
                }
                data.append(result)

        ###############################333
        for i in acc_r:
            credit = 0.0
            debit = 0.0
            acc = ''
            code = ''
            acc_anal = []
            anal = []
            r_anal = []
            for l in list_items:
                acc = l.account_id.name
                code = l.account_id.code
                if l.account_id.id ==i:
                    acc_anal.append(l.analytic_account_id.id)
                    if l.analytic_account_id.id not in anal:
                        anal.append(l.analytic_account_id.id)
                    else:

                        r_anal.append(l.analytic_account_id.id)

            r_anal = list(set(r_anal))
            for l in list_items:

                if l.account_id.id ==i:
                    acc = l.account_id.name
                    code = l.account_id.code

                    credit +=l.credit
                    debit +=l.debit
                    analytic = l.analytic_account_id.name

            result = {
                'acc_analytic': '',
                'debit': debit,
                'credit': credit,
                'acc_name': acc,
                'acc_code': code,
            }


            data.append(result)
            ################################33
            if r_anal:
                count=0
                for x in acc_anal:
                    if x in r_anal:
                        count +=1

                if count==len(acc_anal):
                    result = {
                        'acc_analytic': analytic,
                        'debit': debit,
                        'credit': credit,
                        'acc_name': '',
                        'acc_code': code,
                    }
                    data.append(result)
         ##################################################3
                else:
                    anal_credit=0.0
                    anal_debit = 0.0
                    for y in r_anal:
                        for l in list_items:
                            if l.account_id.id == i and l.analytic_account_id.id == y:

                                anal_credit += l.credit
                                anal_debit += l.debit
                                analytic = l.analytic_account_id.name
                        result = {
                            'acc_analytic': analytic,
                            'debit': anal_debit,
                            'credit': anal_credit,
                            'acc_name': '',
                            'acc_code': '',
                        }
                        data.append(result)
                        ###########################################
                        for l in list_items:
                            if l.account_id.id == i and l.analytic_account_id.id  not in r_anal:
                                result = {
                                    'acc_analytic': l.analytic_account_id.name,
                                    'debit': l.debit,
                                    'credit': l.credit,
                                    'acc_name': '',
                                    'acc_code':'',
                                }
                                data.append(result)

          ####################################################333
            else:
                for a in acc_anal:
                    for l in list_items:
                        if l.account_id.id == i and l.analytic_account_id.id==a:
                            result = {
                                'acc_analytic': l.analytic_account_id.name,
                                'debit': l.debit,
                                'credit': l.credit,
                                'acc_name': '',
                                'acc_code': '',
                            }
                            data.append(result)

        if data:
            return data
        else:
            return {}


    @api.model
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('tt_journal_report.report_financial_position')
        docargs = {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'docs': self.env['account.move'].browse(docids),
            'get_items': self._get_items,
            'sum_credit': self._get_sum_credit,
            'sum_debit': self._get_sum_debit,

        }

        return report_obj.render('tt_journal_report.report_financial_position', docargs)




