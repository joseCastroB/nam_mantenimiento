
from odoo import models, fields, api
from datetime import timedelta

class MantenimientoTiempoOfertada(models.Model):
    _name = 'maintenance.repair.time.offered'
    _description = 'Tiempo Ofertado de Reparación'
    name = fields.Char(string='Tiempo (Semanas)', required=True)

class MantenimientoTipoEquipo(models.Model):
    _name = 'maintenance.equipment.type'
    _description = 'Tipo de Equipo'

    name = fields.Char(string='Nombre', required=True)

class MantenimientoCentroCosto(models.Model):
    _name = 'maintenance.cost.center'
    _description = 'Centro de Costo de Mantenimiento'

    name = fields.Char(string='Nombre', required=True)

class MantenimientoEstatus(models.Model):
    _name = 'maintenance.equipment.status'
    _description = 'Estatus del equipo'

    name = fields.Char(string='Nombre', required=True)

class MantenimientoEquipo(models.Model):
    _inherit = 'maintenance.equipment'

    # SECCION DATOS GENERALES
    name = fields.Char(tracking=True)

    fecha_ingreso = fields.Date(string='Fecha de ingreso', tracking=True)

    garantia = fields.Selection(
        [('si', 'Sí'), ('no', 'No')],
        string='Garantía',
        tracking=True
    )
    
    motivo_ingreso = fields.Text(string='Motivo de ingreso a taller', tracking=True)

    usado_por = fields.Selection([
        ('interno', 'Cliente Interno'),
        ('externo', 'Cliente Externo')

    ], string='Usado por', default='interno', tracking=True)

    fecha_baja = fields.Date(string='Fecha de baja', tracking=True)

    centro_costo = fields.Many2one(
        'maintenance.cost.center',
        string ='Centro de Costo',
        tracking = True
    )

    # LOGISTICA

    area_logistica = fields.Char(string='Área', tracking=True)

    fecha_notificacion_cliente = fields.Date(string='Fecha de notificación de almacén cliente', tracking=True)

    fecha_salida_almacen = fields.Date(string='Fecha de salida de almacén o cita de recojo', tracking=True)

    fecha_ingreso_taller = fields.Date(string='Fecha de ingreso a taller', tracking=True)

    fecha_salida_taller = fields.Date(string='Fecha de salida de taller', tracking=True)

        #transportista_id = fields.Char(string='Transportista / Guia Transporte / Guia NAM', tracking=True)

    guia_transportista = fields.Char(string='Guía de transportista', tracking=True)

    guia_nam = fields.Char(string='Guía NAM', tracking=True)

    fecha_entrega_almacen = fields.Date(string='Fecha de entrega almacén cliente', tracking=True)

    # SECCION INFORMACION DEL PRODUCTO
    coloquial_cliente = fields.Char(string='Coloquial cliente', tracking=True)

   # docs_ingreso = fields.Text(string='Documentos de ingreso de taller', tracking=True)

    model = fields.Char(tracking=True)

    marca = fields.Char(string='Marca', tracking=True)

    serial_no = fields.Char(tracking=True)
    
    tipo_equipo_id = fields.Many2one(
        'maintenance.equipment.type',  
        string='Tipo de Equipo', 
        tracking=True
    )

    propietario_id = fields.Many2one(
        'res.partner',
        string='Propietario',
        tracking=True
    )

    usuario_id = fields.Many2one(
        'res.partner',
        string='Usuario',
        tracking=True
    )

    horas_ingreso = fields.Float(string = 'Horómetro de componente', tracking=True)

    planner_id = fields.Many2one('res.users', string='Planner', tracking=True)

    asesor_id = fields.Many2one(
        'hr.employee',
        string='Asesor Comercial',
        tracking=True
    )

    flota = fields.Selection([
        ('eq_comp_min_50', 'EQ.COMP<50HP'),
        ('eq_comp_max_50', 'EQ.COMP>50HP'),
        ('comp_unitarios', 'COMP.UNITARIOS'),
        ('comp_dobles', 'COMP.DOBLES'),
        ('equipos_varios', 'EQUIPOS VARIOS'),
        ('bombas_min_60', 'BOMBAS<60HP'),
        ('bombas_max_60', 'BOMBAS>60HP')
    ], string='Flota', tracking=True)

    estado_reparacion_id = fields.Selection([
        ('espera_eval', 'ESPERA EVAL'),
        ('evaluacion', 'EVALUACION'),
        ('comercial', 'COMERCIAL'),
        ('devolucion', 'DEVOLUCION'),
        ('espera_po', 'ESPERA PO'),
        ('reparacion', 'REPARACION'),
        ('entregado', 'ENTREGADO'),
        ('terminado', 'TERMINADO')
    ], string='Estado de Reparación', tracking=True)

    edad_dias = fields.Char(
        string='Edad',
        compute='_compute_edad_dias',
        store=False
    )


    @api.depends('fecha_ingreso', 'fecha_real_equipo_listo')
    def _compute_edad_dias(self):
        for record in self:
            if not record.fecha_ingreso:
                record.edad_dias = 'FALTA INGRESO'
            else:
                start_date = record.fecha_ingreso
                
                if not record.fecha_real_equipo_listo:
                    end_date = fields.Date.context_today(record)
                else:
                    end_date = record.fecha_real_equipo_listo
                
                if end_date and start_date:
                    delta = end_date - start_date
                    record.edad_dias = f"{delta.days} días"
                else:
                    record.edad_dias = 'Error Fechas'

    prox_fin = fields.Char(
        string='Prox. Fin', 
        compute='_compute_prox_fin',
        store=False
    )

    @api.depends('eval_fin', 'fecha_real_equipo_listo', 'fecha_fin_prop_eco')
    def _compute_prox_fin(self):
        for record in self: 
            if not record.eval_fin:
                record.prox_fin = "-"
            elif record.fecha_real_equipo_listo:
                record.prox_fin = "-"
            elif not record.fecha_fin_prop_eco:
                record.prox_fin = "FALTA FECHA FIN"
            else:
                today = fields.Date.context_today(record)
                delta = record.fecha_fin_prop_eco - today 
                record.prox_fin = f"{delta.days} días"

    # Sección  Evaluación (fechas)

    eval_inicio = fields.Date(string='Inicio de evaluación', tracking=True)
    eval_fin = fields.Date(string='Fin de evaluación', tracking=True)
    eval_dias = fields.Char(
        string='Eval (días)',
        compute='_compute_eval_días',
        store=False
    )
    @api.depends('eval_inicio', 'eval_fin')
    def _compute_eval_días(self):
        for record in self:
            if not record.eval_inicio and not record.eval_fin:
                record.eval_dias = "PROG. EVAL"
                continue

            if not record.eval_inicio:
                record.eval_dias = "Falta Fecha Inicio"
                continue

            if not record.eval_fin:
                end_date = fields.Date.context_today(record)
            else: 
                end_date = record.eval_fin
            
            start_date = record.eval_inicio

            if start_date > end_date:
                record.eval_dias = "Error: Inicio > Fin"
            else: 
                working_days = 0
                current_date = start_date
                while current_date <= end_date:
                    if current_date.weekday() < 5:
                        working_days += 1
                    current_date += timedelta(days=1)
                record.eval_dias =f"{working_days} días"


    eval_std_tiempo = fields.Integer(
        string='Eval STD Tiempo',
        compute='_compute_eval_std_tiempo',
        store=True
    )

    @api.depends('flota')
    def _compute_eval_std_tiempo(self):
        # Usamos las LLAVES del selection (la parte izquierda)
        tabla_tiempos = {
            "eq_comp_min_50": 6,
            "eq_comp_max_50": 9,
            "comp_unitarios": 5,
            "comp_dobles": 6,
            "equipos_varios": 15,
            "bombas_min_60": 6,
            "bombas_max_60": 9
        }

        for record in self:
            # Ya no necesitamos .upper() ni .strip() porque el valor es fijo
            record.eval_std_tiempo = tabla_tiempos.get(record.flota, 0)

    # Sección PO -> Documentación Comercial

    informe_taller = fields.Date(string='Fecha de informe de taller', tracking=True)
    informe_evaluacion = fields.Date(string='Fecha de informe de evaluación', tracking=True)
    cotizacion = fields.Date(string='Fecha de cotización', tracking=True)
    envio_cotizacion = fields.Date(string='Fecha de envío de cotización e informe al cliente', tracking=True)
    informe_final = fields.Date(string='Fecha de informe final', tracking=True)
    envio_informe_final = fields.Date(string='Fecha de envío de informe final al cliente', tracking=True)
    monto_cotizacion = fields.Float(
        string='Monto de cotización',
        digits = (12, 2),
        tracking=True
    )
    dias_credito = fields.Integer(string='Días de crédito', tracking=True)
    encuesta_satisfaccion = fields.Date(string='Fecha de encuesta de satisfacción', tracking=True)
    respuesta_cliente = fields.Date(string='Fecha de respuesta del cliente', tracking=True)
    estatus_id = fields.Many2one(
        'maintenance.equipment.status',
        string='Estatus', 
        tracking=True
    )


    po_emision = fields.Date(string ='PO Emisión', tracking=True)
    po_recepcion = fields.Date(string = 'PO Recepción', tracking=True )
    po_fin = fields.Date(string = 'PO Fecha de Entrega', tracking=True)

    rfq_core_solped = fields.Char(string='RFQ / CORE / SOLPED', tracking=True)

    tiempo_ofertado_id = fields.Many2one(
        'maintenance.repair.time.offered',
        string='Tiempo ofertado (semanas)',
        tracking=True
    )

    purchase_order = fields.Char(string='PO (Purchase Order)', tracking=True)

    monto_po = fields.Monetary(
        string='Monto PO',
        currency_field='currency_id',
        tracking=True
    )

    currency_id = fields.Many2one(
        'res.currency',
        string ='Moneda',
        required = True,
        default = lambda self: self.env.company.currency_id.id,
        tracking=True
    )

    tasa_cambio = fields.Float(
        string='Tasa de cambio', 
        digits=(12, 3), # (Total dígitos, Decimales)
        tracking=True
    )

    notas_comerciales = fields.Text(string='Notas Comerciales', tracking=True)

    # Garantía

    estatus_id_ga = fields.Many2one(
        'maintenance.equipment.status', 
        string='Estatus', 
        tracking=True
    )

    rfq_core_solped_ga = fields.Char(string='RFQ / CORE / SOLPED', tracking=True)
    purchase_order_ga = fields.Char(string='PO (Purchase Order)', tracking=True)
    analisis_falla_ga = fields.Date(string='Fecha de análisis de falla', tracking=True)
    informe_garantia_ga = fields.Date(string='Fecha de informe de garantía', tracking=True)

    po_fecha_entrega_ga = fields.Date(string='PO Fecha de entrega', tracking=True)
    informe_final_ga = fields.Date(string='Fecha de informe final', tracking=True)
    envio_informe_final_ga = fields.Date(string='Fecha de envío de informe final al cliente', tracking=True)
    encuesta_satisfaccion_ga = fields.Date(string='Fecha de encuesta de satisfacción', tracking=True)
    respuesta_cliente_ga = fields.Date(string='Fecha de respuesta del cliente', tracking=True)

    notas_garantia = fields.Text(string='Notas de Garantía', tracking=True)

    # Fecha inicio reparación

    fecha_inicio_previos = fields.Date(string='Fecha Inicio Previos Reparación', tracking=True)
    fecha_inicio_reparacion = fields.Date(string='Fecha Inicio Reparacion', tracking=True)
    fecha_llegada_kit = fields.Date(string= 'Llegada de Kit', tracking=True)

    # Fecha  fin reparación

    fecha_fin_prop_eco = fields.Date(string='Fin Según Prop. Eco.', tracking=True)
    fecha_fin_gantt = fields.Date(string='Fin Gantt', tracking=True)
    fecha_termino_interno = fields.Date(string='Termino Interno', tracking=True)
    fecha_real_equipo_listo = fields.Date(string='Equipo Listo', tracking=True)

    repair_dias = fields.Integer(
        string='Repair (Días)', 
        compute ='_compute_repair_dias',
        store=True
    )

    @api.depends('fecha_inicio_reparacion', 'fecha_real_equipo_listo')
    def _compute_repair_dias(self):
        for record in self:
            if not record.fecha_inicio_reparacion or not record.fecha_real_equipo_listo:
                record.repair_dias = 0
                continue

            start_date = record.fecha_inicio_reparacion
            end_date = record.fecha_real_equipo_listo

            if start_date > end_date:
                record.repair_dias = 0
            else:
                working_days = 0
                current_date = start_date

                while current_date <= end_date:
                    if current_date.weekday() < 5:
                        working_days += 1
                    current_date += timedelta(days=1)

                record.repair_dias = working_days 


    repair_std_tiempo = fields.Integer(
        string='Repair STD Tiempo (Días)',
        compute='_compute_repair_std_tiempo',
        store=True
    )

    @api.depends('flota')
    def _compute_repair_std_tiempo(self):
        # Usamos las LLAVES del selection
        tabla_tiempos_repair = {
            "eq_comp_min_50": 9,
            "eq_comp_max_50": 12,
            "comp_unitarios": 5,
            "comp_dobles": 8,
            "equipos_varios": 15,
            "bombas_min_60": 12,
            "bombas_max_60": 15
        }

        for record in self:
            record.repair_std_tiempo = tabla_tiempos_repair.get(record.flota, 0)

    fecha_entrega_equipo = fields.Date(string='Entrega de Equipo', tracking=True)

    def _compute_display_name(self):
        for record in self: 
            record.display_name = record.name
