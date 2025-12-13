# -*- coding: utf-8 -*-
from openerp import fields, models, _
# from openerp.exceptions import UserError


class SiatWizardRegister(models.TransientModel):
    """
    creamos este wizard para poder mostrar mensajes ya que al usar botones de tipo object no es posioble lanzar warnings
    """
    _name = "siat.wizard.register"

    name = fields.Char("Nombre Punto de Venta", required=True)
    description = fields.Char("Descripción", required=True)

    system_code = fields.Char(string="Codigo Sistema")
    environment_code = fields.Char(string="Codigo Ambiente")

    branch_code = fields.Integer('Branch Code', default=0)
    mode_constant = fields.Selection([(1, 'ELECTRÓNICA EN LÍNEA'),
                                      (2, 'COMPUTARIZADA EN LÍNEA')], string='Mode Constant', default=2)

    tipo_punto_venta_id = fields.Many2one('tipo.punto.venta', string="Tipo de punto de venta", required=True)
    cuis = fields.Char(string="Codigo CUIS")
    bol_nit = fields.Char(string='Nit')

    def action_create_point_of_sale(self):
        context = self._context
        active_id = context.get('active_id')
        cuis_id = self.env['siat.cuis'].browse(active_id)
        parent_cuis = cuis_id if not cuis_id.parent_cuis else cuis_id.parent_cuis
        obj = self.env['siat.servicio.facturacion.operaciones']
        res = obj.registro_punto_venta(code_type_pdv=self.tipo_punto_venta_id.codigo_clasificador,
                                       description=self.description,
                                       cuis=parent_cuis.cuis,
                                       nit=self.bol_nit,
                                       nombre_puntoventa=self.name)
        if res['transaccion'] == True:
            code = res['codigoPuntoVenta']

            values = {'name': self.name,
                      'bol_is_rts': cuis_id.bol_is_rts,
                      'bol_receipt_title': cuis_id.bol_receipt_title,
                      'bol_invoice_category': cuis_id.bol_invoice_category,
                      'bol_razon_social': cuis_id.bol_razon_social,
                      'bol_entity_title': cuis_id.bol_entity_title or False,
                      'mode_constant': cuis_id.mode_constant,
                      'branch_code': cuis_id.branch_code,
                      'selling_point_code': code,
                      # 'cuis': parent_cuis.cuis,
                      # 'date_validity': cuis_id.date_validity,
                      'company_id': cuis_id.company_id.id,
                      # 'cufd_code': cuis_id.cufd_code,
                      # 'control_code': cuis_id.control_code,
                      'direction': cuis_id.direction,
                      # 'effective_date': cuis_id.effective_date,
                      'parent_cuis': parent_cuis.id,
            }
        cuis_id.company_id.write({'siat_cuis_ids': [(0, 0, values)]})
