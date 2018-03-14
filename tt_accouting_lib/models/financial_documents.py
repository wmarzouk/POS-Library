# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, time, timedelta

class financial_document_type(models.Model):

    _name = 'financial.document.type'
    _inherit = 'mail.thread'
    _description = "Financial Document Type"

    name = fields.Char(string="Document Type",required=True)
    debit_account = fields.Many2one('account.account',string="Debit Account",required=True)
    credit_account = fields.Many2one('account.account', string="Credit Account",required=True)
    short_code = fields.Char(string="Short Code",required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this journal")
    default_journal_id = fields.Many2one('account.journal', string="Journal")



class financial_document(models.Model):

    _name = 'financial.document'
    _inherit = 'mail.thread'
    _description = "Financial Document"

    name = fields.Char(string="Document Number", default="Draft Note",readonly=True)
    partner_id = fields.Many2one('res.partner',required=True)
    state = fields.Selection([('draft','Draft'),('done','Posted'),('recon','Reconciled')],default='draft',track_visibility='onchange')
    note_type = fields.Selection([('debit','Debit'),('credit','Credit')],required=True,readonly=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this journal")
    amount = fields.Monetary(string="Amount",track_visibility='onchange',required=True,currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string="Currecy",default=lambda self: self.env.user.company_id.currency_id)
    doc_type = fields.Many2one('financial.document.type',string="Document Type",required=True)
    note_text = fields.Text(string="Description")
    move_line_id = fields.Many2one('account.move.line',string="Journal Entry")
    doc_create_date = fields.Date(string="Document Date",track_visibility='onchange',required=True,default=fields.Date.today())


    @api.multi
    def validate_doc(self):
        for rec in self:
            if rec.doc_type.default_journal_id:
                journal = rec.doc_type.default_journal_id
            else:
                journal = self.env['account.journal'].search([('name','=','Default Financial Document Journal')])
                if not journal:
                    raise ValidationError(_("Please Define Journal for the Document type or define default Journal with name Default Financial Document Journal"))
            sequence_code = 'financial.document.seq'
            rec.name = self.env['ir.sequence'].next_by_code(sequence_code)
            rec.state = 'done'
            aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
            company_currency = self.company_id.currency_id
            debit, credit, amount_currency, currency_id = aml_obj.with_context(
                date=rec.doc_create_date).compute_amount_fields(rec.amount, rec.currency_id,
                                                             company_currency, False)
            move_name = journal.with_context(ir_sequence_date=fields.Date.today()).sequence_id.next_by_id() or ''
            move_vals = {
                'name': move_name,
                'journal_id': journal.id,
                'date': rec.doc_create_date,
                'company_id': self.company_id.id,
            }
            move = self.env['account.move'].with_context(check_move_validity=False).create(move_vals)
            if rec.note_type =='credit':
                debit_acc_id = rec.doc_type.debit_account.id
                credit_acc_id = rec.partner_id.property_account_receivable_id.id
            else:
                debit_acc_id = rec.partner_id.property_account_payable_id.id
                credit_acc_id = rec.doc_type.credit_account.id
            debit_line_vals = {
                'name': rec.name,
                'account_id': debit_acc_id,
                'partner_id': rec.partner_id.id,
                'debit': debit,
                'credit': credit,
                'amount_currency': amount_currency,
                'currency_id': currency_id,
                'move_id': move.id,
            }
            credit_line_vals = {
                'name': rec.name,
                'account_id': credit_acc_id,
                'partner_id': rec.partner_id.id,
                'debit': credit,
                'credit': debit,
                'amount_currency': -1 * amount_currency,
                'currency_id': currency_id,
                'move_id' : move.id,
            }
            debit_line = aml_obj.create(debit_line_vals)
            credit_line = aml_obj.create(credit_line_vals)
            if rec.note_type =='debit':
                rec.move_line_id = debit_line.id
            else:
                rec.move_line_id = credit_line.id
            move.post()

    @api.onchange('note_type')
    def change_note_type(self):
        if self.note_type and self.note_type=='credit':
            return {'domain': {'partner_id': [('customer', '=', True)]}}
        if self.note_type and self.note_type=='debit':
            return {'domain': {'partner_id': [('supplier', '=', True)]}}
        return True

    @api.multi
    @api.constrains('amount')
    def _check_offer_price(self):
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError(_("Please provide correct Amount"))
