
from odoo import models, fields

class MantenimientoTaller(models.Model):
    _name = 'mantenimiento.taller'
    _description = 'Taller de Mantenimiento'
    name = fields.Char(string='Nombre del Taller', required=True)

class MaintenanceRequest(models.Model):
    
    _inherit = 'maintenance.request'

    tecnico_id = fields.Many2one(
        'res.users',
        string='Técnico',
        tracking=True,
    )
    
    planner_id = fields.Many2one(
        'res.users',
        string='Planner',
        tracking=True,
    )

    taller_id = fields.Many2one(
        'mantenimiento.taller',
        string='Taller',
        
    )