from odoo import models, fields, api

class MaintenanceProductLine(models.Model):
    _name = 'maintenance.request.product.line'
    _description = 'Línea de Repuestos de Mantenimiento'

    request_id = fields.Many2one('maintenance.request', string='Solicitud')
    product_id = fields.Many2one('product.product', string='Repuesto', required=True)
    quantity = fields.Float(string='Cantidad', default=1.0)
    uom_id = fields.Many2one('uom.uom', string='Unidad', related='product_id.uom_id')