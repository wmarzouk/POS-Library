# -*- coding: utf-8 -*-


#      ****************This py is not used now ***********************
#      ****************The file is disabled in init file ***********************

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, time, timedelta
import json
from odoo.tools import float_is_zero, float_compare

class account_inv_inherit(models.Model):


    _inherit = 'account.invoice'

    @api.one
    def _get_outstanding_info_JSON(self):
        res = super(account_inv_inherit,self)._get_outstanding_info_JSON()
        target = open('C:\log.txt', 'a')
        target.write("_get_outstanding_info_JSON:inherit" + "\n")
        target.close()
        # if self.state == 'open':
        #     outstanding_notes = []
        #     if self.type in ('out_invoice', 'in_refund'):
        #         outstanding_notes = self.env['financial.document'].search([('partner_id', '=', self.partner_id.id),
        #                                                                     ('note_type', '=', 'credit'),
        #                                                                           ('state','=','done')])
        #         type_payment = _('Outstanding credits')
        #     else:
        #         outstanding_notes = self.env['financial.document'].search([('partner_id','=',self.partner_id.id),
        #                                                            ('note_type','=','debit'),('state','=','done')])
        #         type_payment = _('Outstanding debits')
        #     if len(outstanding_notes):
        #         info = {'title': type_payment, 'outstanding': True, 'content': [], 'invoice_id': self.id}
        #         for note in outstanding_notes:
        #             if note.move_line_id.currency_id and note.move_line_id.currency_id == self.currency_id:
        #                 amount_to_show = abs(note.move_line_id.amount_residual_currency)
        #             else:
        #                 amount_to_show = note.move_line_id.company_id.currency_id.with_context(date=note.move_line_id.date).compute(abs(note.move_line_id.amount_residual), self.currency_id)
        #             if float_is_zero(amount_to_show, precision_rounding=self.currency_id.rounding):
        #                 continue
        #             if self.outstanding_credits_debits_widget:
        #                 data_dict = json.loads(self.outstanding_credits_debits_widget)
        #                 target = open('C:\log.txt', 'a')
        #                 target.write("outstanding_credits_debits_widget: " + str(self.outstanding_credits_debits_widget) + "\n")
        #                 target.write("data_dict: " + str(data_dict) + "\n")
        #                 target.close()
        #             else:
        #                 info['content'].append({
        #                     'journal_name': note.move_line_id.ref or note.move_line_id.move_id.name,
        #                     'amount': amount_to_show,
        #                     'currency': self.currency_id.symbol,
        #                     'id': note.move_line_id.id,
        #                     'position': self.currency_id.position,
        #                     'digits': [69, self.currency_id.decimal_places],
        #                 })
        #                 self.outstanding_credits_debits_widget = json.dumps(info)
        #                 self.has_outstanding = True
        return res