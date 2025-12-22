
from odoo import models, fields, api
from datetime import timedelta

class MantenimientoTiempoOfertada(models.Model):
    _name = 'maintenance.repair.time.offered'
    _description = 'Tiempo Ofertado de Reparación'
    name = fields.Char(string='Tiempo (Semanas)', required=True)

class MantenimientoEquipo(models.Model):
    _inherit = 'maintenance.equipment'

    coloquial_cliente = fields.Char(string='Coloquial cliente')

    tipo_id = fields.Many2one('mantenimiento.equipo.tipo',  string='Tipo de Equipo')

    fecha_ingreso = fields.Date(string='Fecha de ingreso')

    propietario_id = fields.Many2one(
        'res.partner',
        string='Propietario'
    )

    docs_ingreso = fields.Text(string='Documentos de ingreso de taller')
    horas_ingreso = fields.Float(string = 'Horómetro de componente')

    reingreso = fields.Selection(
        [('si', 'Sí'), ('no', 'No')],
        string='Reingreso'
    )

    motivo_ingreso = fields.Text(string='Motivo de ingreso a taller')

    tasa_cambio = fields.Float(
        string='Tasa de cambio', 
        digits=(12, 3) # (Total dígitos, Decimales)
    )
    
    marca = fields.Char(string='Marca')

    purchase_order = fields.Char(string='PO (Purchase Order)')

    currency_id = fields.Many2one(
        'res.currency',
        string ='Moneda',
        required = True,
        default = lambda self: self.env.company.currency_id.id
    )

    monto_po = fields.Monetary(
        string='Monto PO',
        currency_field='currency_id'
    )

    # Sección Datos de reconocimiento

    planner_id = fields.Many2one('res.users', string='Planner')
    
    flota = fields.Selection([
        ('eq_comp_min_50', 'EQ.COMP<50HP'),
        ('eq_comp_max_50', 'EQ.COMP>50HP'),
        ('comp_unitarios', 'COMP.UNITARIOS'),
        ('comp_dobles', 'COMP.DOBLES'),
        ('equipos_varios', 'EQUIPOS VARIOS'),
        ('bombas_min_60', 'BOMBAS<60HP'),
        ('bombas_max_60', 'BOMBAS>60HP')
    ], string='Flota')

    estado_reparacion_id = fields.Selection([
        ('espera_eval', 'ESPERA EVAL'),
        ('evaluacion', 'EVALUACION'),
        ('comercial', 'COMERCIAL'),
        ('devolucion', 'DEVOLUCION'),
        ('espera_po', 'ESPERA PO'),
        ('reparacion', 'REPARACION'),
        ('entregado', 'ENTREGADO'),
        ('terminado', 'TERMINADO')
    ], string='Estado de Reparación')

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

    eval_inicio = fields.Date(string='Inicio de evaluación')
    eval_fin = fields.Date(string='Fin de evaluación')
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

    # Sección PO

    po_emision = fields.Date(string ='PO Emisión')
    po_recepcion = fields.Date(string = 'PO Recepción' )
    po_fin = fields.Date(string = 'PO Fin')

    # Fecha inicio reparación

    tiempo_ofertado_id = fields.Many2one(
        'maintenance.repair.time.offered',
        string='Tiempo ofertado (semanas)'
    )

    fecha_inicio_previos = fields.Date(string='Fecha Inicio Previos Reparación')
    fecha_inicio_reparacion = fields.Date(string='Fecha Inicio Reparacion')
    fecha_llegada_kit = fields.Date(string= 'Llegada de Kit')

    # Fecha  fin reparación

    fecha_fin_prop_eco = fields.Date(string='Fin Según Prop. Eco.')
    fecha_fin_gantt = fields.Date(string='Fin Gantt')
    fecha_termino_interno = fields.Date(string='Termino Interno')
    fecha_real_equipo_listo = fields.Date(string='Real Equipo Listo')

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

    fecha_entrega_equipo = fields.Date(string='Entrega de Equipo')

    def _compute_display_name(self):
        for record in self: 
            record.display_name = record.name
