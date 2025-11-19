
from odoo import models, fields


class MantenimientoTipo(models.Model):
    _name = 'mantenimiento.equipo.tipo'
    _description = 'Tipo de Equipo Personalizado'

    name = fields.Char(string='Nombre', required=True)


class MantenimientoEquipo(models.Model):
    _inherit = 'maintenance.equipment'


    tipo_id = fields.Many2one(
        'mantenimiento.equipo.tipo', 
        string='Tipo de Equipo'
    )


    currency_id = fields.Many2one(
        'res.currency', 
        string='Moneda'
    )

    tasa_cambio = fields.Float(
        string='Tasa de cambio', 
        digits=(12, 3) # (Total dígitos, Decimales)
    )