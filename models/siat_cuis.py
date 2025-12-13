# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date
from dateutil import parser
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from ..tools import siat_tools as st
import pytz
import logging

_logger = logging.getLogger(__name__)

class SiatCuis(models.Model):
    _name = 'siat.cuis'

    name = fields.Char(string="Nombre")

    bol_is_rts = fields.Boolean(string="Régimen Tributario Simplificado (RTS)",
                                default=False,
                                help="El Servicio Nacional de Impuestos de Bolivia, exime de emitir facturas a personas que tengan un capital menor o igual un determinado monto establecido por ley. \n\n"
                                     "El Régimen Tributario Simplificado (RTS) es lo que el SIN cataloga como personas permitidas a no emitir facturas.\n"
                                     "Caso contrario el Régimen es el GENERAL.")

    bol_receipt_title = fields.Char(string='Título Comprobante',
                                    required=True,
                                    size=50,
                                    default='RECIBO',
                                    help='Título a colocar en el comprobante del PAGO en caso de configurar la compañia como RTS, o al vender sin emitir una factura.')

    bol_invoice_category = fields.Char(string='Category',
                                       size=200,
                                       default='',
                                       help='NIT category for the company')

    bol_razon_social = fields.Char(string='Business name',
                                   required=False,
                                   size=150,
                                   default='',
                                   help="Business name, for example for a 'Empresa Unipersonal': \n"
                                        "'DE: JUAN PEREZ' or 'DE: MARIA FERNANDA SUAREZ'")

    bol_entity_title = fields.Char(string='Entity Title',
                                   required=False,
                                   size=50,
                                   default='',
                                   help="Title for the company entity, example: \n"
                                        "'CASA MATRIZ' or 'SUCURSAL 1'")

    bol_invoice_caption_1 = fields.Text(string='Caption 1', help='First caption for the invoice (RND10-0025-14-SFV)',
                                        default='Esta factura contribuye al desarrollo del país. El uso ilícito de esta será sancionado de acuerdo a ley')

    bol_invoice_caption_2 = fields.Text(string='Caption 2', help='Second caption for the invoice (RND10-0025-14-SFV)',
                                        default='Ley Nro. 453: "El proveedor debe brindar atención sin discriminación, con respeto, calidez y cordialidad a los usuarios y consumidores."')

    bol_invoice_caption_3 = fields.Text(string='Caption 3', help='Third caption for the invoice (RND10-0025-14-SFV)',
                                        default='Este documento es una impresión de un Documento Digital emitido en una Modalidad de Facturación en Línea')

    bol_invoice_caption_4 = fields.Text(string='Caption 4', help='Offline caption for the invoice (RND10-0025-14-SFV)',
                                        default='“Este documento es la Representación Gráfica de un Documento Fiscal Digital emitido fuera de línea, verifique su envío con su proveedor o en la página web www.impuestos.gob.bo”.')

    # Codigo Modalidad
    mode_constant = fields.Selection([(1, 'ELECTRÓNICA EN LÍNEA'),
                                      (2, 'COMPUTARIZADA EN LÍNEA')], string='Mode Constant', default=2)

    # Codigo de Sucursal
    branch_code = fields.Integer('Branch Code', default=0,
                                 help='Valor que identifica a la sucursal donde se realiza la emisión de la Factura: Casa Matriz: 0 Sucursal: 1,2,..,n')

    # CODIGO DE PUNTO DE VENTA
    selling_point_code = fields.Integer('Selling Point Code', default=0,
                                        help='Solo se envía cuando la transacción se realiza utilizando un punto de venta. Caso contrario enviar 0')

    cuis = fields.Char(string="Codigo CUIS")

    date_validity = fields.Datetime(string="Fecha Vigencia ")

    date_obtaining = fields.Datetime(string="Fecha Obtencion ")

    company_id = fields.Many2one('res.company', string='Company', required=True)

    cufd_code = fields.Char(string="Codigo Cufd")

    control_code = fields.Char(string="Codigo Control")

    direction = fields.Char(string="Direccion")

    effective_date = fields.Datetime(string="Fecha Vigencia")

    obtaining_date = fields.Datetime(string="Fecha Obtencion")

    municipality = fields.Char(string="Municipio")

    type_doc_sector = fields.Many2one('documento.sector', string='Documento del sector')

    type_factura = fields.Many2one('tipos.factura', string='Tipo factura')

    evento_significativo = fields.Boolean(string='Fuera de linea', default=False)

    evento_significativo_id = fields.Many2one('eventos.significativos', string='Tipo de Evento')

    parent_cuis = fields.Many2one('siat.cuis', string='Parent Cuis')

    def action_get_information_cuis(self):
        """
        metodo: obtencion de cuis
        return: dic informacion cuis
        """
        company_id = self.env.user.company_id
        obj = self.env['siat.servicio.facturacion.sincronizacion']
        res = obj.action_get_information_cuis(company=company_id, modalidad=self.mode_constant,
                                              sucursal=self.branch_code, puntoventa=self.selling_point_code)
        if 'transaccion' in res and not res['transaccion']:
            str_error = "Se produjo un error en la solicitud de actualizacion del codigo CUIS \n"
            if 'codigo' in res and self.cuis != "0" and self.cuis != str(res['codigo']):
                str_error += "El CUIS EVALUADO NO COINCIDE CON EL CUIS ACTUALMENTE REGISTRADO"

            raise ValidationError(str_error)
        else:
            self.cuis = str(res['codigo'])
            self.date_validity = res['fechaVigencia']
            self.date_obtaining = st.iso_strdt_to_dt_odoo_utc(self.get_information_fecha_hora(),self.env.user.tz)

    def action_get_information_cufd(self):
        """Metodo para ejecutar desde el BOTON 'obtener CUFD' en siat.cuis"""
        #obtenemosla fecha y hora del serivicio de sincronizacion siat
        dt_sin = self.get_information_fecha_hora()
        # en base a la fecha obtenida evaluamos y obtenemos los datos nuevos del cufd
        if not self.effective_date:
            force_cufd = True
        else:
            force_cufd = False
        cufdcc, cufd, dtcufd, _ = self.get_cufd_data(dt_sin, force_cufd)
        if self.cufd_code == cufd and self.control_code == cufdcc:
            return self.env['siat.soap.base'].call_custom_wizard_response('CUFD',
                                                                          'El CUFD {} con fecha de vencimiento {} es valido respecto a la fecha SIN {}'.format(
                                                                              cufdcc, dtcufd, self.iso_strdt_to_dt_odoo(dt_sin)))
        else:
            return self.env['siat.soap.base'].call_custom_wizard_response('CUFD', """El CUFD actual vencio  respecto a la fecha sin {} y se procedio a generar uno nuevo: \n
                                                                                  CUFD: {}\n
                                                                                  Fecha de Vencimiento: {}
                                                                                  """.format(self.iso_strdt_to_dt_odoo(dt_sin), cufdcc, dtcufd))

    def get_information_fecha_hora(self):
        company_id = self.env.user.company_id
        obj = self.env['siat.servicio.facturacion.sincronizacion']
        res = obj.sincronizar_fecha_hora(company=company_id, cuis=self.cuis, sucursal=self.branch_code,
                                         puntoventa=self.selling_point_code)
        if 'fechaHora' in res:
            return res['fechaHora']
        else:
            return False

    def action_get_informationfecha_hora(self):
        dt = self.get_information_fecha_hora()
        if dt:
            title = 'Fecha y Hora'
            message = str(dt)
            return self.env['siat.soap.base'].call_custom_wizard_response(title, message)

    def get_cufd_data(self, dt_sin, force_cufd=False):
        """
        creamos un metodo para obtener el cufd, evaluando siempre la fecha de vencimiento del cufd actual
        la idea es obtener la fecha de impuestos nacionales y comparar con la fecha vigente del cifd
        en el caso de que la fecha de sin sea mayor a la del cufd traemos un nuevo cufd
        en el caso de que la fecha de sin sea mayor a la del cufd traemos un nuevo cufd
        Outpur: tupla => codigo de control, codigo CUFD, fecha calidez CUFD usr_tz, fecha calidez CUFD UTC_tz
        """
        # obtenemos el dt del sin y primero lo convertimos de iso_string_datetime a datetime
        # luego le añadimos el timezone del usuario
        sin_dt = self.add_user_tz_to_dt(self.iso_strdt_to_dt_odoo(dt_sin))
        # obtenemos el dt de fecha de validez del cufd con tz del usuario
        if self.effective_date:
            cufd_dt = self.get_cufd_effective_dt_on_usr_tz()
            #comparamos si el sin_dt es mayor al cufd_dt
            # TODO: para produccione ste codigo debe estar descomentado
            if sin_dt > cufd_dt:
                # en el caso de que sin_dt es mayor al cufd_dt obtenemos un nuevo CUFD
                self.get_new_cufd()
            else:
                if force_cufd:
                    self.get_new_cufd()
        else:
            self.get_new_cufd()
        # ya sea si trajimos o no un nuevo CUFD, devolvemos la informacion actual que se tiene almacenada del CUFD
        cufdcc = self.control_code
        cufd = self.cufd_code
        cufdt = self.get_cufd_effective_dt_on_usr_tz()
        return (cufdcc, cufd, cufdt, self.effective_date)

    def get_new_cufd(self):
        """
        metodo: obtencion de cufd
        return: dic informacion cufd
        """
        company_id = self.env.user.company_id
        obj = self.env['siat.servicio.facturacion.sincronizacion']
        try:
            res = obj.action_get_information_cufd(cuis=self.cuis,
                                                  company=company_id,
                                                  modalidad=self.mode_constant,
                                                  sucursal=self.branch_code,
                                                  puntoventa=self.selling_point_code)
        except ValidationError as exc:
            # Si recibimos un error de validación del servicio (por ejemplo 966)
            _logger.warning("action_get_information_cufd devolvió ValidationError: %s", str(exc))
            # Crear evento significativo para dejar constancia y permitir seguimiento manual
            try:
                # buscar tipo de evento que represente error/caída de servicio (código 2 por convención)
                event_type = self.env['eventos.significativos'].search([('codigo_clasificador', '=', 2)], limit=1)
                ev_vals = {
                    'siat_cuis_id': self.id,
                    'company_id': self.company_id.id,
                    'cuis': self.cuis or False,
                    'cufd': self.cufd_code or False,
                    'branch_code': self.branch_code,
                    'selling_point_code': self.selling_point_code,
                    'evento_significativo_id': event_type.id if event_type else False,
                    'descripcion': u"Error al solicitar CUFD: %s" % (str(exc),),
                    'date_start': self.get_information_fecha_hora() or fields.Datetime.now(),
                    'date_end': self.get_information_fecha_hora() or fields.Datetime.now(),
                    'state': 'failed',
                }
                self.env['siat.eventos.significativos'].create(ev_vals)
            except Exception as ce:
                _logger.error("No se pudo crear siat.eventos.significativos tras fallo CUFD: %s", str(ce))

            # Re-levantar la excepción para que la capa superior decida (o retornar para fallback según política).
            raise
        except Exception as e:
            _logger.exception("Error inesperado al pedir CUFD: %s", str(e))
            raise

        # Si la respuesta fue exitosa continuamos con el código existente
        if res['transaccion']:
            dt_reg = st.add_utc_tz_to_dt(res['fechaVigencia']) if res['fechaVigencia'].tzinfo is None else st.convert_dt_tz_to_utc_tz(res['fechaVigencia'])
            self.update({
                'cufd_code': str(res['codigo']),
                'control_code': str(res['codigoControl']),
                'direction': res['direccion'],
                'effective_date': dt_reg
            })
            self.obtaining_date = st.iso_strdt_to_dt_odoo_utc(self.get_information_fecha_hora(), self.env.user.tz)
            # registramos el historial de cufd
            self.env['historial.cufd'].create({'name': self.id,
                                               'cufd_code': str(res['codigo']),
                                               'control_code': str(res['codigoControl']),
                                               'direction': res['direccion'],
                                               'effective_date': dt_reg,
                                               'cuis': self.cuis,
                                               'branch_code': self.branch_code,
                                               'selling_point_code': self.selling_point_code})
    def strdt_utc_to_dt_usr_tz(self, strdt):
        """
        metodo para convertir un string_datetime a un datetime con tz del usuario
        """
        # validamos que strdt sea de tipo string
        self.string_validation(strdt)
        # convertimos el string a datetime
        dt = self.convert_strdt_to_datetime(strdt)
        # obtenemos el tz del usuario
        local_tz = pytz.timezone(self.env.user.tz) if self.env.user.tz else pytz.utc
        # devolvemos el dt en UTC al tz del usuario
        return self.convert_dt_tz_to_custom_tz(self.add_utc_tz_to_dt(dt), local_tz)

    def convert_strdt_to_datetime(self, strdt, tzformat="%Y-%m-%d %H:%M:%S"):
        """
        metodo para convertir un string_datetime a un datetime
        *****
        si se requiere podemos enviar un formato especifico, pero como formato por defecto usamos '%Y-%m-%d %H:%M:%S'
        """
        return datetime.strptime(strdt, tzformat)

    def convert_dt_tz_to_custom_tz(self, dt, tz):
        """metodo para convertir un dt con tz UTC a un tz diferente
        parametros de entrada:
        dt = dato de tipo datetime con timezone
        tz = objeto timezone instanciadmo mediate pytz
        """
        # validamos que dt sea de tipo datetime
        self.dt_type_validation(dt)
        return dt.astimezone(tz)

    def add_user_tz_to_dt(self, dt):
        """metodo para añadir un tz del usuario a un dt sin tz"""
        # validamos que dt sea de tipo datetime
        self.dt_type_validation(dt)
        self.tz_validation(dt)
        local_tz = pytz.timezone(self.env.user.tz) if self.env.user.tz else pytz.utc
        return local_tz.localize(dt, is_dst=None)

    def add_utc_tz_to_dt(self, dt):
        """metodo para añadir un tz UTC a un dt sin tz"""
        # validamos que dt sea de tipo datetime
        self.dt_type_validation(dt)
        self.tz_validation(dt)
        return pytz.utc.localize(dt, is_dst=None)

    def get_cufd_effective_dt_on_usr_tz(self):
        """metodo para obtener la fecha de validez del CUFD en tz del usuario"""
        return self.strdt_utc_to_dt_usr_tz(self.effective_date)

    def iso_strdt_to_dt_odoo(self, strdt):
        """metodo para convertirr un string_dt_ISO 'yyyy-MM-dd'T'HH:mm:ss.SSSXXX' a dt"""
        return parser.parse(strdt)

    def tz_validation(self, dt):
        """
        validamos que el dt no tenga timezone
        """
        if dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None:
            raise ValidationError("La fecha ya contiene timezone")

    def dt_type_validation(self, dt):
        """
        validamos que dt sea de tipo datetime
        """
        if not isinstance(dt, datetime):
            raise ValidationError("El dato ingresado no es de tipo datetime")

    def string_validation(self, string):
        """
        validamos que dt sea de tipo datetime
        """
        if not isinstance(string, str):
            raise ValidationError("El dato ingresado no es de tipo cadena")

    def action_register_point_of_sale(self):
        company_id = self.env.user.company_id
        return {
            'name': "Registro de Punto de Venta",
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'views': [(self.env.ref('siat_sin_bolivia.siat_wizard_register_form_view').id, 'form')],
            'res_model': 'siat.wizard.register',
            'type': 'ir.actions.act_window',
            'context': {'default_bol_nit': str(company_id.siat_nit),
                        'default_cuis': self.cuis,
                        'default_branch_code': self.branch_code,
                        'default_system_code': str(company_id.system_code),
                        'default_mode_constant': self.mode_constant,
                        'default_environment_code': company_id.environment_code}
        }

    def action_close_point_of_sale(self):
        cuis = self if not self.parent_cuis else self.parent_cuis
        obj = self.env['siat.servicio.facturacion.operaciones']
        res = obj.cierre_punto_venta(company_id=self.company_id,
                                     selling_point_code=self.selling_point_code,
                                     cuis=cuis.cuis)
        if res['transaccion'] == True:
            self.unlink()
            return self.env['siat.soap.base'].call_custom_wizard_response('Punto de venta ' + str(res['codigoPuntoVenta']), 'Cerrado')
        else:
            return self.env['siat.soap.base'].call_custom_wizard_response('La operacion', 'Fallo')

    def close_operation_system(self):
        if self.parent_cuis:
            raise ValidationError("Es metodo solo puede ser llamado desde el cuis principal:\n" + self.parent_cuis.name)
        obj = self.env['siat.servicio.facturacion.operaciones']
        obj.cierre_operaciones_sistema(company_id=self.company_id,
                                       cuis=self.cuis,
                                       branch_code=self.branch_code,
                                       selling_point_code=self.selling_point_code)
        return True


