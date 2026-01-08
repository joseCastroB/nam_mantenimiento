from odoo import models, fields, api
from odoo.exceptions import ValidationError
from markupsafe import Markup
import logging

_logger = logging.getLogger(__name__)

class MantenimientoTaller(models.Model):
    _name = 'mantenimiento.taller'
    _description = 'Taller de Mantenimiento'
    

class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    # Campos de cabecera
    name = fields.Char(tracking=True)
    # BLOQUEAR CAMPO "CREADO POR" (EMPLOYEE)
    # Al redefinirlo aquí con readonly=True, se bloquea en todas las vistas automáticamente
    equipment_id = fields.Many2one('maintenance.equipment', tracking=True)

    employee_id = fields.Many2one('hr.employee', string='Creado por', readonly=True)

    fecha_creacion_custom = fields.Date(
        string='Fecha de Creación', 
        default=fields.Date.context_today,
        readonly=True
    )
    fecha_programacion_custom = fields.Date(string='Fecha de Programación', tracking=True)

    descripcion_corta = fields.Char(string='Descripción', tracking=True)

    hrs = fields.Float(string='HRS', default=0.0, tracking=True)
    tec = fields.Float(string='TEC', default=0.0, tracking=True)

    hh = fields.Float(
        string='HH',
        compute='_compute_hh',
        store=True,
        readonly=True
    )

    comentario_solicitud = fields.Text(string='Comentario')

    repuesto_line_ids = fields.One2many(
        'maintenance.request.product.line',
        'request_id',
        string='Repuestos Requeridos',
        tracking=True
    )

    def action_consumir_repuestos(self):
        for record in self:
            if not record.repuesto_line_ids:
                continue

            # Log para el chat
            msg = "<b>Iniciando proceso de descuento de stock...</b><br/>"

            # 1. Definir ubicaciones
            # Usamos las referencias XML ID estándar de Odoo
            location_src_id = self.env.ref('stock.stock_location_stock').id
            location_dest_id = self.env.ref('stock.stock_location_customers').id
            
            # 2. Buscar tipo de albarán de salida
            picking_type = self.env['stock.picking.type'].search([('code','=','outgoing')], limit=1)
            
            # 3. Crear la Cabecera del Albarán (Picking)
            picking = self.env['stock.picking'].create({
                'picking_type_id': picking_type.id,
                'location_id': location_src_id,
                'location_dest_id': location_dest_id,
                'origin': record.name,
            })

            moves_created = False

            # 4. Crear Movimientos (Líneas)
            for line in record.repuesto_line_ids:
                prod = line.product_id
                
                # CAMBIO CLAVE: Aceptamos todo lo que NO sea servicio
                # Así incluimos 'consu' (Bienes) y 'product' (Almacenable)
                if prod.type != 'service':
                    self.env['stock.move'].create({
                        'name': prod.name,
                        'product_id': prod.id,
                        'product_uom_qty': line.quantity,
                        'product_uom': prod.uom_id.id,
                        'picking_id': picking.id,
                        'location_id': location_src_id,
                        'location_dest_id': location_dest_id,
                    })
                    moves_created = True
                    msg += f"- {prod.name}: <span class='text-success'>OK (Procesado)</span><br/>"
                else:
                    msg += f"- {prod.name}: <span class='text-danger'>OMITIDO (Es un Servicio)</span><br/>"

            # 5. Validar si hubo movimientos reales
            if moves_created:
                try:
                    # Confirmar
                    picking.action_confirm()
                    # Asignar disponibilidad
                    picking.action_assign()
                    
                    # Truco: Forzar la cantidad realizada para no tener que entrar al picking
                    for move in picking.move_ids:
                        move.quantity = move.product_uom_qty

                    # Validar (Kardex)
                    picking.button_validate()
                    
                    msg += f"<br/><b>¡Éxito!</b> Stock descontado. Albarán: <a href='#' data-oe-model='stock.picking' data-oe-id='{picking.id}'>{picking.name}</a>"
                except Exception as e:
                    msg += f"<br/><b>Error al validar:</b> {str(e)}"
            else:
                # Si no se creó nada, borramos el picking vacío
                picking.unlink()
                msg += "<br/><b>Aviso:</b> No se generó ningún movimiento."

            # Publicar resultado en el chat
            record.message_post(body=Markup(msg))

    resumen_repuestos = fields.Char(
        string='Repuestos',
        compute='_compute_resumen_repuestos'
    )

    @api.depends('repuesto_line_ids', 'repuesto_line_ids.product_id')
    def _compute_resumen_repuestos(self):
        for record in self:
            nombres = [line.product_id.name for line in record.repuesto_line_ids if line.product_id]
            record.resumen_repuestos = ", ".join(nombres) if nombres else ""


    @api.depends('hrs', 'tec')
    def _compute_hh(self):
        for record in self:
            record.hh = record.hrs * record.tec

    tecnico_id = fields.Many2many(
        'res.users',
        string='Técnico',
        help = "Permite seleccionar múltiples técnicos para esta orden",
        tracking=True
    )

    programador_id = fields.Many2one(
        'res.users', 
        string='Programador',
        default = lambda self: self.env.user,
        readonly=True
    )
    
    taller_id = fields.Many2one('mantenimiento.taller',  string='Taller', tracking=True)

    bahia = fields.Selection([
        ('1', '1'),
        ('2', '2'),
        ('U','U')
    ], string='Bahía', help='Seleccione el código de Bahía para el formato de impresión') 

    # Seccion Notificado

    hh_real = fields.Float(string='HH Real', default=0.0, tracking=True)

    porcentaje_completado = fields.Float(string='% Completado Tarea', default=0.0, tracking=True)

    @api.constrains('porcentaje_completado')
    def _check_porcentaje_valido(self):
        for record in self:
            if record.porcentaje_completado < 0.0 or record.porcentaje_completado > 1.0:
                raise ValidationError("El porcentaje debe ser un número entre 0 y 100.")

    fecha_notificacion = fields.Date(string='Fecha Notificación', tracking=True)

    comentario_notificacion = fields.Text(string='Comentario Notificación', tracking=True)
    
    # ---------------------------------------------------------
    # MÉTODO CREATE (Optimizado para Odoo 18)
    # ---------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            sequence = self.env['ir.sequence'].next_by_code('secuencia.mantenimiento.nam') or '000000'
            nombre_equipo = ''
            if vals.get('equipment_id'):
                equipment = self.env['maintenance.equipment'].browse(vals['equipment_id'])
                nombre_equipo = equipment.name
            
            if nombre_equipo:
                vals['name'] = f"{nombre_equipo} / {sequence}"
            else: 
                vals['name'] = sequence

        requests = super(MaintenanceRequest, self).create(vals_list)

        for req in requests:
            gerente_id = req.user_id.id if req.user_id else False
            project = self.env['project.project'].create({
                'name': req.name,
                'user_id': gerente_id,
                'allow_timesheets': True,
            })

            analytic_account = self.env['account.analytic.account'].search([
                ('name', '=', project.name)
            ], limit=1)

            tasa_cambio = 1.0
            if req.equipment_id:
                tasa_cambio = getattr(req.equipment_id, 'tasa_cambio', 1.0)
                if tasa_cambio <= 0: tasa_cambio = 1.0

                if analytic_account:
                    analytic_account.write({'tasa_cambio': tasa_cambio})

            task = self.env['project.task'].create({
                'name': 'Horas Hombre',
                'project_id': project.id,
                'user_ids': req.tecnico_id.ids if req.tecnico_id else [],
            })

            if req.tecnico_id and req.hrs > 0 and analytic_account:
                for user in req.tecnico_id:
                    employee = self.env['hr.employee'].search([('user_id', '=', user.id)], limit=1)
                    
                    if employee:
                        costo_hora = employee.hourly_cost or 0.0
                        total_base = costo_hora * req.hrs
                        costo_final = total_base / tasa_cambio

                        timesheet = self.env['account.analytic.line'].create({
                            'name': 'Horas Hombre',
                            'project_id': project.id,
                            'task_id': task.id,
                            'account_id': analytic_account.id,
                            'employee_id': employee.id,
                            'unit_amount': req.hrs,
                            'date': fields.Date.today(),
                        })

                        # --- PASO CRÍTICO: OBLIGAR A ODOO A GUARDAR SU "500" AHORA ---
                        # Esto vacía la memoria de Odoo al disco antes de que nosotros toquemos nada.
                        self.env['account.analytic.line'].flush_model()

                        # --- AHORA SÍ, SOBRESCRIBIMOS CON SQL ---
                        self.env.cr.execute("""
                            UPDATE account_analytic_line
                            SET amount = %s
                            WHERE id = %s
                        """, (-costo_final, timesheet.id))

                        # Limpiamos caché para que la pantalla lea el valor nuevo de la BD
                        timesheet.invalidate_recordset(['amount'])
                        
                        _logger.warning(f"NAM_DEBUG (Create): ID={timesheet.id} corregido a {-costo_final}")

        return requests

    def write(self, vals):
        res = super(MaintenanceRequest, self).write(vals)

        for req in self:
            project = self.env['project.project'].search([('name', '=', req.name)], limit=1)
            
            if project:
                if 'user_id' in vals:
                    project.write({'user_id': vals['user_id']})
                
                analytic_account = self.env['account.analytic.account'].search([
                    ('name', '=', project.name)
                ], limit=1)

                tasa_cambio = 1.0
                if req.equipment_id:
                    tasa_cambio = getattr(req.equipment_id, 'tasa_cambio', 1.0)
                    if tasa_cambio <= 0: tasa_cambio = 1.0
                    
                    if analytic_account:
                        analytic_account.write({'tasa_cambio': tasa_cambio})

                if 'tecnico_id' in vals or 'hrs' in vals or 'equipment_id' in vals:
                    
                    task = self.env['project.task'].search([
                        ('project_id', '=', project.id),
                        ('name', '=', 'Horas Hombre')
                    ], limit=1)

                    if task:
                        task.write({'user_ids': [(6, 0, req.tecnico_id.ids)]})

                        if analytic_account:
                            existing_lines = self.env['account.analytic.line'].search([
                                ('task_id', '=', task.id),
                                ('name', '=', 'Horas Hombre')
                            ])
                            existing_lines.unlink()

                            if req.hrs > 0:
                                for user in req.tecnico_id:
                                    employee = self.env['hr.employee'].search([('user_id', '=', user.id)], limit=1)
                                    
                                    if employee:
                                        costo_hora = employee.hourly_cost or 0.0
                                        total_base = costo_hora * req.hrs
                                        costo_final = total_base / tasa_cambio

                                        timesheet = self.env['account.analytic.line'].create({
                                            'name': 'Horas Hombre',
                                            'project_id': project.id,
                                            'task_id': task.id,
                                            'account_id': analytic_account.id,
                                            'employee_id': employee.id,
                                            'unit_amount': req.hrs,
                                            'date': fields.Date.today(),
                                        })

                                        # --- FLUSH ANTES DEL SQL ---
                                        self.env['account.analytic.line'].flush_model()

                                        self.env.cr.execute("""
                                            UPDATE account_analytic_line
                                            SET amount = %s
                                            WHERE id = %s
                                        """, (-costo_final, timesheet.id))

                                        timesheet.invalidate_recordset(['amount'])

        return res