
from odoo import models, fields

class MaintenanceRequest(models.Model):
    
    _inherit = 'maintenance.request'

    tecnico_id = fields.Many2one(
        'res.users',
        string='Técnico',
    )
    
    planner_id = fields.Many2one(
        'res.users',
        string='Planner',
    )