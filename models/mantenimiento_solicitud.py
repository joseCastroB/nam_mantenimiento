
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
        tracking=True,
    )

    @api.model
    def create(self, vals):

        sequence = self.env['ir.sequence'].next_by_code('secuencia.mantenimiento.nam') or '000000'
        
        nombre_equipo = ''
        if vals.get('equipment_id'):
            equipment = self.env['maintenance.equipment'].browse(vals['equipment_id'])
            nombre_equipo = equipment.name
        
        if nombre_equipo:
            vals['name'] = f"{nombre_equipo} / {sequence}"
        else: 
            vals['name'] = sequence
            
        return super(MaintenanceRequest, self).create(vals)