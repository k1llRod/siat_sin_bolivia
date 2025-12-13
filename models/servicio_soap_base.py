# -*- coding: utf-8 -*-
import logging

from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

try:
    from suds.client import Client
except (ImportError, IOError) as err:
    _logger.debug(err)


class SiatSoapBase(models.TransientModel):
    _name = 'siat.soap.base'

    @api.multi
    def connect_soap(self, wsdl):
        client = Client(wsdl)
        return client

    def connect_wsdl(self, wsdl=False, api_key=False):
        if not wsdl:
            wsdl = self.get_default_service_target()
        try:
            client = self.connect_soap(wsdl)
            if api_key:
                client.set_options(headers={'apikey': 'TokenApi ' + str(self.env.user.company_id.delegated_token)})
            res = True, client
        except Exception as e:
            res = False, e
        return res

    def get_default_service_target(self):
        """Implementar al extender el modelo"""
        return False

    def call_custom_wizard_response(self, title, message):
        """este metodo se encarga de llamar un wizard que mostrara un mensaje customizado en un wizard"""
        return {
            'name': _("Response"),
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'views': [(self.env.ref('siat_sin_bolivia.siat_wizard_resp_view').id, 'form')],
            'res_model': 'siat.wizard.resp',
            'context': {'default_title': title, 'default_message': message},
            'type': 'ir.actions.act_window',
        }

    def check_transaction(self, res):
        if res and 'transaccion' in res and res['transaccion']:
            return True
        else:
            return False

    def check_response(self, res):
        if res and 'transaccion' in res:
            if res['transaccion'] == True:
                return res
            elif res['transaccion'] == False:
                str_error = 'ERROR: \n'
                for msj in res['mensajesList']:
                    str_error += str(msj['codigo']) + ' - ' + msj['descripcion'] + '\n'
                raise ValidationError(str_error)
        else:
            return False

    def msj_conexion_test(self, res):
        if res:
            return self.call_custom_wizard_response('Servicio Facturacion', 'Conexion exitosa')
        else:
            return self.call_custom_wizard_response('Servicio Facturacion', 'Conexion fallida')

    def conection_validation(self, connection, client):
        if not connection:
            # TODO al parecer hubo cambios en como se instanciaba el servicio debemos revisar como debe actuar este metodo o quitarlo
            # raise ValidationError(('La conexion con el servicio de Impuestos Nacionales no se encuentra diponible, \nEspere unos minutos para intentar nuevamente\n Detalle de conexion: \n%s') % client)
            return False

    def validate_response(self, res, force_msj=False):
        str_error = False
        if res['transaccion'] and not force_msj:
            return res['transaccion'], str_error
        if not res['transaccion'] or force_msj:
            str_error = 'ERROR: \n'
            for msj in res['mensajesList']:
                str_error += str(msj['codigo']) + ' - ' + msj['descripcion'] + '\n'
            return res['transaccion'], str_error
