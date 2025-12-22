from odoo import fields, models

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    tasa_cambio = fields.Float(string="Tasa de cambio", digits=(12, 3))