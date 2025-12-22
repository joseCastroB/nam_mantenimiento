from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # ---------------------------------------------------------
    # 1. AUTOMATIZACIÓN: ASIGNAR PROYECTO AL CREAR
    # ---------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # Si tiene origen (OT) pero no Proyecto, buscamos uno con el mismo nombre
            if not vals.get('project_id') and vals.get('origin'):
                # Buscamos proyecto que se llame igual al documento origen (ej. ES8-21-ANT...)
                project = self.env['project.project'].search([('name', '=', vals['origin'])], limit=1)
                if project:
                    vals['project_id'] = project.id
                    
        return super(StockPicking, self).create(vals_list)

    # ---------------------------------------------------------
    # 2. AUTOMATIZACIÓN: GENERAR COSTOS AL VALIDAR
    # ---------------------------------------------------------
    def _action_done(self):
        res = super(StockPicking, self)._action_done()
        
        for picking in self:
            if picking.project_id:
                
                # Buscamos la cuenta analítica
                target_analytic_account = self.env['account.analytic.account'].search([
                    ('name', '=', picking.project_id.name)
                ], limit=1)

                if target_analytic_account:
                    
                    # Obtenemos la Tasa de Cambio
                    tasa_cambio = target_analytic_account.tasa_cambio
                    
                    # Obtenemos la moneda de la compañía del albarán (ej. 'PEN', 'USD')
                    moneda_origen = picking.company_id.currency_id.name

                    for move in picking.move_ids_without_package:
                        cantidad_real = move.quantity 
                        
                        if cantidad_real > 0:
                            # Costo Base en moneda de la compañía (Soles)
                            costo_base = cantidad_real * move.product_id.standard_price
                            costo_final = costo_base
                            
                            # Descripción base
                            descripcion = f"Consumo: {move.product_id.name} ({picking.name})"

                            # --- LÓGICA DE CONVERSIÓN ---
                            # Si es Soles y hay tasa, convertimos a Dólares
                            if moneda_origen == 'PEN' and tasa_cambio and tasa_cambio > 0:
                                costo_final = costo_base / tasa_cambio

                                # TRUCO VISUAL: Agregamos la conversión a la descripción
                                # Esto ayuda a entender que el monto, aunque diga S/, son Dólares.
                                descripcion += f" [Conv. USD: {costo_base:.2f} / {tasa_cambio:.3f}]"
                            # Si la moneda NO es PEN (ej. es USD), el costo pasa directo sin dividir.

                            if costo_final > 0:
                                self.env['account.analytic.line'].create({
                                    'name': descripcion,
                                    'account_id': target_analytic_account.id,
                                    'date': picking.date_done or fields.Date.today(),
                                    'amount': -costo_final, # Guardamos el monto final (negativo)
                                    'unit_amount': cantidad_real,
                                    'product_id': move.product_id.id,
                                    'ref': picking.name,
                                    'company_id': picking.company_id.id,
                                })

        return res