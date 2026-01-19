from odoo import models, fields, api 
from odoo.tools import format_date

class MantenimientoProgramacion(models.Model):
    _name = 'maintenance.daily.program'
    _description = 'Programación Diaria de Mantenimiento'
    _rec_name = 'fecha_programacion'

    user_id = fields.Many2one(
        'res.users', 
        string='Líder'
    )
    
    programador_id = fields.Many2one(
        'res.users', 
        string='Planificador'
    )

    fecha_programacion = fields.Date(string = 'Fecha', default=fields.Date.context_today, required=True)

    fecha_visual = fields.Char(
        string='Fecha',
        compute='_compute_fecha_visual'
    )

    @api.depends('fecha_programacion')
    def _compute_fecha_visual(self):
        for record in self:
            if record.fecha_programacion:
                fecha_str = format_date(self.env, record.fecha_programacion, date_format="EEEE d 'de' MMMM, y")
                record.fecha_visual = fecha_str.capitalize()
            else:
                record.fecha_visual = ""

    bahia = fields.Selection([
        ('MONTAJE', 'MONTAJE'),
        ('TALLER', 'TALLER'), 
        ('DESMONTAJE', 'DESMONTAJE'),
        ('ELECTRICO', 'ELECTRICO'),
        ('FUERA DE TALLER', 'FUERA DE TALLER')
    ], string = 'Bahía / Formato', required=True)

    request_ids = fields.Many2many(
        'maintenance.request',
        string = 'Órdenes de Trabajo'
    )

    horas_disponibles = fields.Float(string='Horas Disponibles', default=0.0)

    horas_visual= fields.Char(
        string='Horas Programadas',
        compute='_compute_horas_visual'
    )

    @api.depends('horas_programadas')
    def _compute_horas_visual(self):
        for record in self:
            record.horas_visual = "{:.2f}".format(record.horas_programadas)

    horas_programadas = fields.Float(string='Horas Programadas', compute ='_compute_totales')
    horas_restantes = fields.Float(string='Horas Restantes', compute='_compute_totales')

    @api.depends('request_ids', 'request_ids.hh', 'horas_disponibles')
    def _compute_totales(self):
            for record in self: 
                total_hh = sum(req.hh for req in record.request_ids)
                record.horas_programadas = total_hh
                record.horas_restantes = record.horas_disponibles - total_hh
    
    name = fields.Char(string='Referencia', compute='_compute_name')

    @api.depends('fecha_programacion', 'bahia')
    def _compute_name(self):
        for record in self:
            fecha = record.fecha_programacion or 'Sin Fecha'
            bahia = dict(self._fields['bahia'].selection).get(record.bahia) or 'Sin Bahía'
            record.name = f"Prog: {fecha} - {bahia}"

    iso_codigo = fields.Char(string='Código ISO', default='NAM-PR-C-03-05')
    iso_fecha = fields.Date(string='Fecha ISO', default=fields.Date.context_today)
    iso_revision = fields.Char(string='Revisión', default='1')

    can_edit_iso = fields.Boolean(compute='_compute_can_edit_iso')

    @api.depends_context('uid')
    def _compute_can_edit_iso(self):
        group_calidad = self.env.ref('nam_mantenimiento.group_gestor_calidad', raise_if_not_found=False)
        user = self.env.user

        for record in self: 
            if group_calidad and group_calidad in user.groups_id:
                  record.can_edit_iso = True
            else:
                 record.can_edit_iso = False