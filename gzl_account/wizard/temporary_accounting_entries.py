# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import ValidationError


class TemporaryAccountingEntries(models.TransientModel):
    _name = 'temporary.accounting.entries'

    
    account_id = fields.Many2one('account.account', 'Cuenta')
    name = fields.Char('Codigo')
    debit = fields.Float( 'Credito')
    credit = fields.Float( 'Debito')


