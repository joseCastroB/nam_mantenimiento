# C:/Users/hp/odoo-dev/custom-addons/mi_modulo_mantenimiento/models/mantenimiento_solicitud.py

from odoo import models, fields

class MaintenanceRequest(models.Model):
    # Heredamos el modelo de solicitud de mantenimiento
    _inherit = 'maintenance.request'

    # Campo para seleccionar al Técnico
    tecnico_id = fields.Many2one(
        'res.users',
        string='Técnico',
    )
    
    # Campo para seleccionar al Planner
    planner_id = fields.Many2one(
        'res.users',
        string='Planner',
    )