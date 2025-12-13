# -*- coding: utf-8 -*-
import random
from odoo import api, fields, models, _


class ProductosServicios(models.Model):

    _name = "productos.servicios"
    _description = 'Sincronizar lista de productos servicios'

    codigo_actividad = fields.Integer(string="Codigo Actividad")
    codigo_producto = fields.Integer(string="Codigo Producto")
    descripcion_producto = fields.Char(string="Descripcion")

    @api.multi
    def name_get(self):
        return [(line.id, '%s - %s' % (line.codigo_actividad, line.descripcion_producto)) for line in self]


class SincronizarAbstract(models.AbstractModel):

    _name = 'sincronizar.abstract'
    _description = 'Modelo Base'

    codigo_clasificador = fields.Integer(string="Codigo Clasificador")
    descripcion = fields.Char(string="Descripcion")

    @api.multi
    def name_get(self):
        return [(line.id, '%s - %s' % (line.codigo_clasificador, line.descripcion)) for line in self]


class CodigosActividades(models.Model):

    #TODO: no encontre el modelo donde se guarda las actividades, por favor revisar si no estoy duplicando

    _name = 'codigos.actividades'
    _description = 'Lista de codigos de actividades'
    # _inherit = 'sincronizar.abstract'
    codigo_caeb = fields.Char(string="Codigo")
    descripcion = fields.Char(string="Descripcion")
    tipo_actividad = fields.Char(string="Tipo de actividad")

    @api.multi
    def name_get(self):
        return [(line.id, '%s - %s' % (line.codigo_caeb, line.descripcion)) for line in self]


class MensajesServicios(models.Model):

    _name = 'mensajes.servicios'
    _description = 'Lista de mensajes servicios'
    # _inherit = 'sincronizar.abstract'
    codigo_clasificador = fields.Integer(string="Codigo Clasificador")
    descripcion = fields.Char(string="Descripcion")

    @api.multi
    def name_get(self):
        return [(line.id, '%s - %s' % (line.codigo_clasificador, line.descripcion)) for line in self]

class EventosSignificativos(models.Model):

    _name = 'eventos.significativos'
    _description = 'Parametrica eventos significativos'
    _inherit = 'sincronizar.abstract'


class MotivoAnulacion(models.Model):

    _name = 'motivo.anulacion'
    _description = 'Parametrica motivo anulacion'
    _inherit = 'sincronizar.abstract'


class PaisOrigen(models.Model):

    _name = 'pais.origen'
    _description = 'Parametrica pais origen'
    _inherit = 'sincronizar.abstract'


class DocumentoIdentidad(models.Model):

    _name = 'documento.identidad'
    _description = 'Tipo Documento Identidad'
    _inherit = 'sincronizar.abstract'


class DocumentoSector(models.Model):
    """Códigos de Tipo Documento Sector"""
    _name = 'documento.sector'
    _description = 'Tipo Documento Identidad'
    _inherit = 'sincronizar.abstract'


class TipoEmision(models.Model):

    _name = 'tipo.emision'
    _description = 'Tipo Emision'
    _inherit = 'sincronizar.abstract'


class TipoHabitacion(models.Model):

    _name = 'tipo.habitacion'
    _description = 'Tipo Habitacion'
    _inherit = 'sincronizar.abstract'


class TipoMetodoPago(models.Model):

    _name = 'tipo.metodo.pago'
    _description = 'Tipo Metodo Pago'
    _inherit = 'sincronizar.abstract'


class TipoMoneda(models.Model):

    _name = 'tipo.moneda'
    _description = 'Tipo Metodo Pago'
    _inherit = 'sincronizar.abstract'


class TipoPuntoVenta(models.Model):

    _name = 'tipo.punto.venta'
    _description = 'Tipo Punto Venta'
    _inherit = 'sincronizar.abstract'


class TiposFactura(models.Model):

    _name = 'tipos.factura'
    _description = 'Tipos Factura'
    _inherit = 'sincronizar.abstract'


class UnidadMedida(models.Model):

    _name = 'unidad.medida'
    _description = 'Unidad Medida'
    _inherit = 'sincronizar.abstract'


class LeyendasFacturas(models.Model):

    _name = 'leyenda.factura'
    _description = 'Leyendas de Facturas'

    codigo_actividad = fields.Integer(string="Codigo Actividad")
    descripcion_leyenda = fields.Char(string="Descripcion")

    @api.multi
    def name_get(self):
        return [(line.id, '%s - %s' % (line.codigo_actividad, line.descripcion_leyenda[:10])) for line in self]

    def get_random_record(self, int_codigo_actividad=False):
        """
        input:
        int_codigo_actividad = Integer
        output:
        model or False
        """
        if int_codigo_actividad:
            records = self.search([('codigo_actividad', "=", int_codigo_actividad)])
        else:
            records = self.search([])
        if records and len(records) > 0:
            return random.choice(records)
        else:
            return False


class ActividadesDocumentoSector(models.Model):

    _name = 'actividades.documento.sector'
    _description = 'Codigos de Actividades Documento Sector'

    codigo_actividad = fields.Char(string="Codigo Actividad")
    codigo_documento_sector = fields.Integer(string="Codigo Documento Sector", default=0)
    tipo_documento_sector = fields.Char(string="Tipo Documento Sector")

    @api.multi
    def name_get(self):
        return [(line.id, '%s - %s - %s' % (line.codigo_actividad, str(line.codigo_documento_sector), line.tipo_documento_sector)) for line in self]
