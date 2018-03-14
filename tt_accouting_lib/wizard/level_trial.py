# -*- coding: utf-8 -*-

from odoo import fields, models


class LevelBalanceReport(models.TransientModel):
    _inherit = "account.common.account.report"
    _name = 'account.level.balance.report'
    _description = 'Level Trial Balance Report'

    def _print_report(self, data):
        data = self.pre_print_report(data)
        records = self.env[data['model']].browse(data.get('ids', []))
        return self.env['report'].get_action(records, 'account.report_trialbalance', data=data)
