
from odoo import models, fields, api

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

    @api.model
    def create(self, vals):
        
        if vals.get('equipment_id'):
            
            equipment = self.env['maintenance.equipment'].browse(vals['equipment_id'])
            
            sequence = self.env['ir.sequence'].next_by_code('maintenance.request.nam') or '000000'
            
            vals['name'] = f"{equipment.name} / {sequence}"
        
        elif not vals.get('name') or vals.get('name') == 'New Request':
             sequence = self.env['ir.sequence'].next_by_code('maintenance.request.nam') or '000000'
             vals['name'] = sequence
             
        return super(MaintenanceRequest, self).create(vals)