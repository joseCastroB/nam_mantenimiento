from odoo import models, fields, api
from markupsafe import Markup

class MaintenanceProductLine(models.Model):
    _name = 'maintenance.request.product.line'
    _description = 'Línea de Repuestos de Mantenimiento'
    
    name = fields.Char(compute='_compute_name', store=True)

    @api.depends('product_id', 'quantity')
    def _compute_name(self):
        for line in self: 
            prod_name = line.product_id.name or 'Sin Producto'
            
            qty = int(line.quantity) if line.quantity.is_integer() else line.quantity
            line.name = f"{prod_name} ({qty})"

    request_id = fields.Many2one('maintenance.request', string='Solicitud')
    product_id = fields.Many2one('product.product', string='Repuesto', required=True)
    quantity = fields.Float(string='Cantidad', default=1.0)
    uom_id = fields.Many2one('uom.uom', string='Unidad', related='product_id.uom_id')

    # 1. DETECTAR CAMBIO DE CANTIDAD (O cualquier otro campo)
    def write(self, vals):
        # Antes de guardar, capturamos los valores viejos
        old_qtys = {rec.id: rec.quantity for rec in self}
        
        # Guardamos los cambios
        result = super(MaintenanceProductLine, self).write(vals)
        
        # Si se modificó la cantidad, avisamos al padre
        if 'quantity' in vals:
            for line in self:
                old_qty = old_qtys.get(line.id)
                new_qty = line.quantity
                
                # Solo avisamos si hubo un cambio real
                if old_qty != new_qty:
                    # Formateamos números bonitos
                    o_qty = int(old_qty) if old_qty.is_integer() else old_qty
                    n_qty = int(new_qty) if new_qty.is_integer() else new_qty
                    
                    msg = Markup(f"✏️ <b>Repuesto Modificado:</b> {line.product_id.name} <br/>Cantidad: {o_qty} &#8594; {n_qty}")
                    
                    # Enviamos el mensaje al historial de la SOLICITUD (Padre)
                    line.request_id.message_post(body=msg)
        
        return result

    # 2. DETECTAR ELIMINACIÓN
    def unlink(self):
        for line in self:
            # Capturamos el dato antes de que se borre
            qty = int(line.quantity) if line.quantity.is_integer() else line.quantity
            msg = Markup(f"🗑️ <b>Repuesto Eliminado:</b> {line.product_id.name} (Cant: {qty})")
            
            # Avisamos al padre
            line.request_id.message_post(body=msg)
            
        return super(MaintenanceProductLine, self).unlink()