# -*- coding: utf-8 -*-
from openerp import fields, api, models, _


class CancelInvoiceSiat(models.TransientModel):
    _name = "cancel.invoice.siat"

    motivo_anulacion_id = fields.Many2one('motivo.anulacion', string='Motivo de anulacion')

    def action_assign_cancel_invoice_siat(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        obj = self.env['siat.servicio.facturacion']
        for record in self.env['account.invoice'].browse(active_ids):
            res = obj.anulacion_factura(company_id=record.company_id,
                                        code_doc_sector=record.siat_codigo_documento_sector,
                                        code_emition=record.siat_codigo_emision.codigo_clasificador,
                                        cuis=record.siat_invoice_channel,
                                        type_invo_doc=str(record.siat_invoice_channel.type_factura.codigo_clasificador),
                                        code_motivo=self.motivo_anulacion_id.codigo_clasificador,
                                        cuf=record.siat_cuf)
