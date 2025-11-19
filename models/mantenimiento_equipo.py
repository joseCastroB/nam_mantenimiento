# C:/Users/hp/odoo-dev/custom-addons/mi_modulo_mantenimiento/models/mantenimiento_equipo.py

from odoo import models, fields

# 1. Creamos un modelo nuevo para los "Tipos"
# Esto permite que guardes nuevos tipos escribiéndolos directamente.
class MantenimientoTipo(models.Model):
    _name = 'mantenimiento.equipo.tipo'
    _description = 'Tipo de Equipo Personalizado'

    name = fields.Char(string='Nombre', required=True)

# 2. Heredamos el equipo de mantenimiento
class MantenimientoEquipo(models.Model):
    _inherit = 'maintenance.equipment'

    # CAMBIO: Ahora 'tipo' es un Many2one al modelo de arriba.
    # Esto permite seleccionar uno existente O crear uno nuevo.
    tipo_id = fields.Many2one(
        'mantenimiento.equipo.tipo', 
        string='Tipo de Equipo'
    )

    # Eliminamos 'categoria_custom' simplemente no definiéndolo aquí.

    # NUEVOS CAMPOS:
    # Moneda: Se conecta a las monedas activas de Odoo
    currency_id = fields.Many2one(
        'res.currency', 
        string='Moneda'
    )

    # Tasa de cambio: Campo numérico con decimales
    tasa_cambio = fields.Float(
        string='Tasa de cambio', 
        digits=(12, 3) # (Total dígitos, Decimales)
    )