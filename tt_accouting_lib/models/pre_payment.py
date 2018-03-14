# -*- coding: utf-8 -*-


from odoo import models, fields, api, _

from odoo.exceptions import Warning,UserError,ValidationError

class inherit_account_payment(models.Model):

    _inherit = 'account.payment'


    account_id = fields.Many2one('account.account' , string = 'Account')
    settle = fields.Boolean(string="settlement",default=False)

    @api.one
    @api.depends('invoice_ids', 'payment_type', 'partner_type', 'partner_id')
    def _compute_destination_account_id(self):

        comp = super(inherit_account_payment, self)._compute_destination_account_id()

        if self.account_id.id and self.settle is not True:
            self.destination_account_id = self.account_id.id

        return comp

    def _get_move_vals(self, journal=None):

        """ Return dict to create the payment move
        """
        journal = journal or self.journal_id
        if not journal.sequence_id:
            raise UserError(_('Configuration Error !'),
                            _('The journal %s does not have a sequence, please specify one.') % journal.name)
        if not journal.sequence_id.active:
            raise UserError(_('Configuration Error !'), _('The sequence of journal %s is deactivated.') % journal.name)
        name = self.move_name or journal.with_context(ir_sequence_date=self.payment_date).sequence_id.next_by_id()

        # in case of settling make sequance increment
        if self.account_id.id and self.settle is True:
            name = journal.with_context(ir_sequence_date=self.payment_date).sequence_id.next_by_id()


        return {
            'name': name,
            'date': self.payment_date,
            'ref': self.communication or '',
            'company_id': self.company_id.id,
            'journal_id': journal.id,
        }

    def _get_liquidity_move_line_vals(self, amount):

        name = self.name
        if self.payment_type == 'transfer':
            name = _('Transfer to %s') % self.destination_journal_id.name
        acc=self.payment_type in ('outbound',
                                  'transfer') and self.journal_id.default_debit_account_id.id or self.journal_id.default_credit_account_id.id,

        # in case of settling pre_payment account become source account
        if self.account_id.id and self.settle is True:
            acc=self.account_id.id
        vals = {
            'name': name,
            'account_id':acc,
            'payment_id': self.id,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
        }

        # If the journal has a currency specified, the journal item need to be expressed in this currency
        if self.journal_id.currency_id and self.currency_id != self.journal_id.currency_id:
            amount = self.currency_id.with_context(date=self.payment_date).compute(amount, self.journal_id.currency_id)
            debit, credit, amount_currency, dummy = self.env['account.move.line'].with_context(
                date=self.payment_date).compute_amount_fields(amount, self.journal_id.currency_id,
                                                              self.company_id.currency_id)
            vals.update({
                'amount_currency': amount_currency,
                'currency_id': self.journal_id.currency_id.id,
            })

        return vals


    @api.multi
    def settl(self):
        self.settle=True

        self.state='draft'
        self.post()

class inherit_accountmoveline(models.Model):
    _inherit = 'account.move.line'


    @api.multi
    def reconcile(self, writeoff_acc_id=False, writeoff_journal_id=False):
        # Perform all checks on lines
        company_ids = set()
        all_accounts = []
        partners = set()
        for line in self:
            company_ids.add(line.company_id.id)
            all_accounts.append(line.account_id)
            if (line.account_id.internal_type in ('receivable', 'payable')):
                partners.add(line.partner_id.id)
            if line.reconciled:
                raise UserError(_('You are trying to reconcile some entries that are already reconciled!'))
        if len(company_ids) > 1:
            raise UserError(_('To reconcile the entries company should be the same for all entries!'))
        if len(set(all_accounts)) > 1:
            raise UserError(_('Entries are not of the same account!'))

        if not line.payment_id.account_id:
            print line.payment_id.account_id
            if not all_accounts[0].reconcile:
                raise UserError(_('The account %s (%s) is not marked as reconciliable !') % (
                all_accounts[0].name, all_accounts[0].code))
        if len(partners) > 1:
            raise UserError(_('The partner has to be the same on all lines for receivable and payable accounts!'))

        # reconcile everything that can be
        remaining_moves = self.auto_reconcile_lines()

        # if writeoff_acc_id specified, then create write-off move with value the remaining amount from move in self
        if writeoff_acc_id and writeoff_journal_id and remaining_moves:
            all_aml_share_same_currency = all([x.currency_id == self[0].currency_id for x in self])
            writeoff_vals = {
                'account_id': writeoff_acc_id.id,
                'journal_id': writeoff_journal_id.id
            }
            if not all_aml_share_same_currency:
                writeoff_vals['amount_currency'] = False
            writeoff_to_reconcile = remaining_moves._create_writeoff(writeoff_vals)
            # add writeoff line to reconcile algo and finish the reconciliation
            remaining_moves = (remaining_moves + writeoff_to_reconcile).auto_reconcile_lines()
            return writeoff_to_reconcile
        return True






