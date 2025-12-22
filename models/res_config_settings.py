from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    process_invoice_automatically = fields.Boolean(string="Procesar Factura Automáticamente")

    process_cancel_posted_invoice_automatically = fields.Boolean(string="Cancelar facturas publicadas automáticamente")

    l10n_pe_edi_provider_ose_without_vat = fields.Boolean(string="Proveedor OSE sin IGV")