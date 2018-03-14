# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, time, timedelta
import json
from odoo.tools import float_is_zero, float_compare

class account_account_inherit(models.Model):


    _inherit = 'account.account'

    parent_id = fields.Many2one('account.account', string='Parent Account')
    child_ids = fields.One2many('account.account', 'parent_id', string="Sub-Accounts")
    level = fields.Integer(string="Level")

    @api.multi
    @api.onchange('parent_id')
    def level_comp(self):
        for rec in self:
            if rec.parent_id:
                if rec.parent_id.level:
                    rec.level = rec.parent_id.level + 1
                else:
                    rec.level = 1
            else:
                rec.level = 1