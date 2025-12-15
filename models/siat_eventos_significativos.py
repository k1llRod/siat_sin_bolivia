# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
from ..tools import siat_tools
import base64
from datetime import date, datetime
from datetime import datetime, timedelta
import pytz
import logging



class SiatEventosSignificativos(models.Model):

    _name = 'siat.eventos.significativos'


    siat_cuis_id = fields.Many2one('siat.cuis', string='Siat Cuis', readonly=True, states={'draft': [('readonly', False)], 'send': [('readonly', False)]})
    company_id = fields.Many2one('res.company', string='Compañia', readonly=True, states={'draft': [('readonly', False)], 'send': [('readonly', False)]})
    environment_code = fields.Selection([(1, 'PRODUCCIÓN'), (2, 'PRUEBAS')], string='Enviroment Code', related='company_id.environment_code', readonly=True, states={'draft': [('readonly', False)], 'send': [('readonly', False)]})
    system_code = fields.Char('System Code', related='company_id.system_code', readonly=True, states={'draft': [('readonly', False)], 'send': [('readonly', False)]})
    siat_nit = fields.Char('NIT', required=True, related='company_id.siat_nit', readonly=True, states={'draft': [('readonly', False)], 'send': [('readonly', False)]})
    cuis = fields.Char('CUIS', readonly=True, states={'draft': [('readonly', False)], 'send': [('readonly', False)]})
    cufd = fields.Char('CUFD', readonly=True, states={'draft': [('readonly', False)], 'send': [('readonly', False)]})
    branch_code = fields.Integer('Branch Code', default=0, related='siat_cuis_id.branch_code', readonly=True, states={'draft': [('readonly', False)], 'send': [('readonly', False)]})
    selling_point_code = fields.Integer('Selling Point Code', default=0, readonly=True, states={'draft': [('readonly', False)], 'send': [('readonly', False)]})
    evento_significativo_id = fields.Many2one('eventos.significativos', readonly=True, states={'draft': [('readonly', False)], 'send': [('readonly', False)]})
    descripcion = fields.Char(string="Descripcion", readonly=True, states={'draft': [('readonly', False)], 'send': [('readonly', False)]})
    date_start = fields.Datetime(string='Fecha Inicio Evento', readonly=True, states={'draft': [('readonly', False)], 'send': [('readonly', False)]})
    date_end = fields.Datetime(string='Fecha Fin Evento', readonly=True, states={'draft': [('readonly', False)], 'send': [('readonly', False)]})
    cufd_event = fields.Char(string='Cufd Evento', readonly=True, states={'draft': [('readonly', False)], 'send': [('readonly', False)]})
    state = fields.Selection([('draft', 'Borrador'),
                              ('send', 'Evento registrado'),
                              ('validated', 'Evento validado'),
                              ('failed', 'Fallido'),], default='draft')
    reception_code = fields.Char(string='Codigo de recepcion', readonly=True, states={'draft': [('readonly', False)], 'send': [('readonly', False)]})
    package_reception_code = fields.Char(string='Codigo de recepcion paquete factura', readonly=True, states={'draft': [('readonly', False)], 'send': [('readonly', False)]})
    invoice_ids = fields.One2many('account.invoice', 'siat_evento_significativo_id', string='Facturas', readonly=True, states={'draft': [('readonly', False)], 'send': [('readonly', False)]})
    tar_file = fields.Binary(string="Tar", readonly=True, states={'draft': [('readonly', False)], 'send': [('readonly', False)]})
    tar_filename = fields.Char(string="Tar", readonly=True, states={'draft': [('readonly', False)], 'send': [('readonly', False)]})
    package_sent = fields.Boolean("Paquete enviado", default=False)
    siat_cafc = fields.Char(string="Cafc", states={'draft': [('readonly', False)], 'send': [('readonly', False)]})


    # @api.model
    # def create(self, vals):
    #     res = super(SiatEventosSignificativos, self).create(vals)
    #     # if res.evento_significativo_id.codigo_clasificador in [5, 6, 7]:
    #     #     res.cufd_event = self.env['historial.cufd'].get_my_date_cufd(res.siat_cuis_id.id, res.cuis, res.branch_code,res.selling_point_code, res.date_start)
    #     return res

    _logger = logging.getLogger(__name__)
    def action_register_event_significant(self):
        """
                Envía al SIN las facturas asociadas a este evento significativo
                (corte de internet / tipo_emisión = 2) mediante recepcionPaqueteFactura.
                Se asume que las facturas ya fueron marcadas como offline y tienen XML+CUF.
                """
        self.ensure_one()

        channel = self.siat_cuis_id
        company = self.company_id

        if not channel:
            raise UserError(_("Canal SIAT (CUIS) no definido."))

        if not self.reception_code:
            # self.action_register_event_significant()
            if not self.reception_code:
                raise ValidationError(u"El evento significativo no devolvió código de recepción del SIN.")

        # 2) Facturas pendientes de enviar en este evento
        invoices = self.invoice_ids.filtered(
            lambda inv: inv.siat_offline
                        and not inv.siat_codigo_recepcion
                        and inv.siat_xml_file
        )

        if not invoices:
            raise ValidationError(u"No hay facturas offline pendientes de enviar para este evento.")

        # 3) Generar TAR (paquete) con los XML de las facturas
        xml_files = [inv.siat_xml_file for inv in invoices]
        tar_file_b64 = siat_tools.action_generator_file_tar(xml_files)
        # ya viene en base64 en tu helper; si no, lo conviertes:
        # tar_file_b64 = base64.b64encode(tar_file)

        # 4) Hash del archivo
        hash_256 = siat_tools.action_generator_hash(tar_file_b64, 'hash_256')

        # 5) Fecha de envío (ahora mismo, el SIN tolera mucha más diferencia en paquetes)
        send_date = channel.get_information_fecha_hora()  # usa tu helper que ya da fecha en formato correcto

        # 6) Llamar al servicio recepcion_paquete_factura
        service = self.env['siat.servicio.facturacion']

        res = service.recepcion_paquete_factura(
            company_id=company,
            code_doc_sector=channel.type_doc_sector.codigo_clasificador,
            code_emition=2,  # SIEMPRE 2 para fuera de línea
            mode_constant=channel.mode_constant,
            selling_point_code=channel.selling_point_code,
            branch_code=channel.branch_code,
            cufd=channel.cufd_code,  # CUFD asociado al evento
            cuis=channel.cuis,
            type_invo_doc=channel.type_factura,
            archivo=tar_file_b64,
            send_date=send_date,
            hash_archivo=hash_256,
            cafc=None,  # o tu campo si manejas CAFC
            qty_facturas=len(invoices),
            code_event=self.reception_code  # codigoRecepcionEventoSignificativo
        )

        # 7) Interpretar respuesta
        #   check_response de tu servicio ya debería normalizar dict/objeto;
        #   asumo que devuelve un dict con 'transaccion' y 'codigoRecepcion'
        if isinstance(res, dict):
            trans_ok = res.get('transaccion', False)
            package_reception_code = res.get('codigoRecepcion')
            mensajes = res.get('mensajesList')
        else:
            trans_ok = getattr(res, 'transaccion', False)
            package_reception_code = getattr(res, 'codigoRecepcion', None)
            mensajes = getattr(res, 'mensajesList', None)

        if not trans_ok:
            msg = u"El SIN no aceptó el paquete offline."
            if isinstance(mensajes, list) and mensajes:
                first = mensajes[0]
                if isinstance(first, dict):
                    msg = first.get('descripcion', msg)
                else:
                    msg = getattr(first, 'descripcion', msg)
            raise ValidationError(msg)

        # 8) Marcar paquete como enviado y actualizar facturas
        self.write({
            'package_sent': True,
            'package_reception_code': str(package_reception_code or ''),
        })

        invoices.write({
            'siat_offline': False,
            'siat_codigo_recepcion': str(package_reception_code or ''),
        })

        return True

    def register_package_invoices(self, company, invoices, channel, code_event):
        send_date = channel.get_information_fecha_hora()
        if len(invoices) == 0:
            raise ValidationError("No hay facturas para procesar")
        if len(invoices) > 500:
            raise ValidationError("No se puede procesar mas de 500 facturas")
        tar_file = siat_tools.action_generator_file_tar([x.siat_xml_file for x in invoices])
        self.tar_file = tar_file
        # gun_zip = siat_tools.generate_file_gzip(self.tar_file, 'paquete.tar.gz')
        # convertimos el gzip en binary
        gun_zip_binary = tar_file
        # gun_zip_binary = self.tar_file

        self.tar_filename = 'paquete.tar.gz'
        hash_256 = siat_tools.action_generator_hash(self.tar_file, 'hash_256')

        obj = self.env['siat.servicio.facturacion']
        res = obj.recepcion_paquete_factura(company_id=company,
                                            code_doc_sector=channel.type_doc_sector.codigo_clasificador,
                                            code_emition=2,
                                            mode_constant=channel.mode_constant,
                                            selling_point_code=channel.selling_point_code,
                                            branch_code=channel.branch_code,
                                            cufd=channel.cufd_code,
                                            cuis=channel.cuis,
                                            type_invo_doc=channel.type_factura,
                                            archivo=gun_zip_binary,
                                            send_date=send_date,
                                            hash_archivo=hash_256,
                                            cafc=None if not self.siat_cafc else self.siat_cafc,
                                            qty_facturas=len(invoices),
                                            code_event=code_event)
        if 'transaccion' in res and res['transaccion']:
            self.write({'package_reception_code': str(res['codigoRecepcion']),
                        'package_sent': True})

    def action_inv_package_receipt_validation(self):
        self.inv_package_receipt_validation(self.company_id,
                                            self.siat_cuis_id,
                                            self.package_reception_code)

    def inv_package_receipt_validation(self, company, channel, pkg_code):
        obj = self.env['siat.servicio.facturacion']
        res = obj.validacion_recepcion_paquete_factura(company_id=company,
                                                       code_doc_sector=channel.type_doc_sector.codigo_clasificador,
                                                       code_emition=2, #TODO:talvez deberiamos de parametrizar
                                                       mode_constant=channel.mode_constant,
                                                       selling_point_code=channel.selling_point_code,
                                                       branch_code=channel.branch_code,
                                                       cufd=channel.cufd_code,
                                                       cuis=channel.cuis,
                                                       type_invo_doc=channel.type_factura.codigo_clasificador,
                                                       code_reception=pkg_code)
        if 'transaccion' in res and res['transaccion']:
            if 'codigoEstado' in res and res['codigoEstado'] == 908:
                self.write({'state': 'validated'})
            else:
                _, msj = obj.validate_response(res, force_msj=True)
                raise ValidationError(str(res['codigoEstado']) + ' ' + str(res['codigoDescripcion']) + '\n' + msj)

    def action_consulta_evento_significativo(self):
        self.ensure_one()
        # Validar datos mínimos
        if not self.date_start or not self.siat_cuis_id:
            raise ValidationError("Datos insuficientes: debe definir fecha y canal SIAT (CUIS).")
        # Convertir fecha desde UTC (Odoo) a TZ usuario y luego a yyyy-mm-dd
        dt_usr = siat_tools.strdt_utc_to_dt_usr_tz(self.date_start, self.env.user.tz)
        event_date = dt_usr.strftime('%Y-%m-%d')
        return self.consulta_evento_significativo(self.siat_cuis_id, event_date)

    def consulta_evento_significativo(self, channel, event_date):
        """
            Consulta eventos significativos registrados en el SIN para una fecha dada.
            Muestra los códigos de recepción en un wizard.
            """
        obj = self.env['siat.servicio.facturacion.operaciones']
        if not channel:
            raise ValidationError("No se ha definido el canal / CUIS SIAT para la consulta de eventos.")

        if not event_date:
            raise ValidationError("Debe especificar una fecha para la consulta de eventos.")
        res = obj.consulta_evento_significativo(channel=channel, event_date=event_date)
        # Normalizar respuesta: dict u objeto
        if isinstance(res, dict):
            trans_ok = res.get('transaccion', False)
            codigos = res.get('listaCodigos') or res.get('listaEventos') or []
            mensajes_list = res.get('mensajesList')
        else:
            trans_ok = getattr(res, 'transaccion', False)
            codigos = getattr(res, 'listaCodigos', []) or getattr(res, 'listaEventos', [])
            mensajes_list = getattr(res, 'mensajesList', None)

        if not trans_ok:
            # Intentar extraer mensaje de error del SIN
            error_msg = 'Error desconocido'
            if isinstance(mensajes_list, list) and mensajes_list:
                first = mensajes_list[0]
                if isinstance(first, dict):
                    error_msg = first.get('descripcion', error_msg)
                else:
                    error_msg = getattr(first, 'descripcion', error_msg)

            raise ValidationError("Error consultando eventos significativos: %s" % error_msg)

        # Construir texto con los códigos de recepción
        lines = []

        for elem in codigos:
            if isinstance(elem, dict):
                codigo = elem.get('codigoRecepcionEventoSignificativo') or elem.get('codigoRecepcion')
                fecha_ini = elem.get('fechaInicio') or elem.get('fechaHoraInicioEvento')
                fecha_fin = elem.get('fechaFin') or elem.get('fechaHoraFinEvento')
            else:
                codigo = (
                        getattr(elem, 'codigoRecepcionEventoSignificativo', None)
                        or getattr(elem, 'codigoRecepcion', None)
                )
                fecha_ini = getattr(elem, 'fechaInicio', None) or getattr(elem, 'fechaHoraInicioEvento', None)
                fecha_fin = getattr(elem, 'fechaFin', None) or getattr(elem, 'fechaHoraFinEvento', None)

            line = "codigoRecepcionEventoSignificativo: %s" % (codigo or '')
            if fecha_ini or fecha_fin:
                line += " | desde: %s hasta: %s" % (fecha_ini or '-', fecha_fin or '-')
            lines.append(line)

        if not lines:
            lines.append("Sin eventos significativos registrados para la fecha %s." % event_date)

        message = "\n".join(lines)

        return obj.call_custom_wizard_response('Servicio Facturacion', message)

    @api.multi
    def action_send_offline_invoices_no_internet(self):
        """
        Envía al SIN las facturas asociadas a este evento significativo
        (corte de internet / tipo_emisión = 2) mediante recepcionPaqueteFactura.
        Se asume que las facturas ya fueron marcadas como offline y tienen XML+CUF.
        """
        self.ensure_one()

        channel = self.siat_cuis_id
        company = self.company_id

        if not channel:
            raise ValidationError(u"No se ha definido el canal SIAT (CUIS) para el evento significativo.")

        # 1) Asegurarnos que el evento esté registrado en el SIN
        if not self.reception_code:
            # reutilizas tu función existente para registrar el evento
            self.action_register_event_significant()
            if not self.reception_code:
                raise ValidationError(u"El evento significativo no devolvió código de recepción del SIN.")

        # 2) Facturas pendientes de enviar en este evento
        invoices = self.invoice_ids.filtered(
            lambda inv: inv.siat_offline
                        and not inv.siat_codigo_recepcion
                        and inv.siat_xml_file
        )

        if not invoices:
            raise ValidationError(u"No hay facturas offline pendientes de enviar para este evento.")

        # 3) Generar TAR (paquete) con los XML de las facturas
        xml_files = [inv.siat_xml_file for inv in invoices]
        tar_file_b64 = siat_tools.action_generator_file_tar(xml_files)
        # ya viene en base64 en tu helper; si no, lo conviertes:
        # tar_file_b64 = base64.b64encode(tar_file)

        # 4) Hash del archivo
        hash_256 = siat_tools.action_generator_hash(tar_file_b64, 'hash_256')

        # 5) Fecha de envío (ahora mismo, el SIN tolera mucha más diferencia en paquetes)
        send_date = channel.get_information_fecha_hora()  # usa tu helper que ya da fecha en formato correcto

        # 6) Llamar al servicio recepcion_paquete_factura
        service = self.env['siat.servicio.facturacion']

        res = service.recepcion_paquete_factura(
            company_id=company,
            code_doc_sector=channel.type_doc_sector.codigo_clasificador,
            code_emition=2,  # SIEMPRE 2 para fuera de línea
            mode_constant=channel.mode_constant,
            selling_point_code=channel.selling_point_code,
            branch_code=channel.branch_code,
            cufd=channel.cufd_code,  # CUFD asociado al evento
            cuis=channel.cuis,
            type_invo_doc=channel.type_factura,
            archivo=tar_file_b64,
            send_date=send_date,
            hash_archivo=hash_256,
            cafc=None,  # o tu campo si manejas CAFC
            qty_facturas=len(invoices),
            code_event=self.reception_code  # codigoRecepcionEventoSignificativo
        )

        # 7) Interpretar respuesta
        #   check_response de tu servicio ya debería normalizar dict/objeto;
        #   asumo que devuelve un dict con 'transaccion' y 'codigoRecepcion'
        if isinstance(res, dict):
            trans_ok = res.get('transaccion', False)
            package_reception_code = res.get('codigoRecepcion')
            mensajes = res.get('mensajesList')
        else:
            trans_ok = getattr(res, 'transaccion', False)
            package_reception_code = getattr(res, 'codigoRecepcion', None)
            mensajes = getattr(res, 'mensajesList', None)

        if not trans_ok:
            msg = u"El SIN no aceptó el paquete offline."
            if isinstance(mensajes, list) and mensajes:
                first = mensajes[0]
                if isinstance(first, dict):
                    msg = first.get('descripcion', msg)
                else:
                    msg = getattr(first, 'descripcion', msg)
            raise ValidationError(msg)

        # 8) Marcar paquete como enviado y actualizar facturas
        self.write({
            'package_sent': True,
            'package_reception_code': str(package_reception_code or ''),
        })

        invoices.write({
            'siat_offline': False,
            'siat_codigo_recepcion': str(package_reception_code or ''),
        })

        return True

    @api.multi
    def action_register_event_significant(self):
        """
        Registra el evento significativo en el SIN y guarda:
        - reception_code = codigoRecepcionEventoSignificativo
        Cambia el estado a 'send' si OK, o 'failed' si error.
        """
        self.ensure_one()

        if not self.siat_cuis_id:
            raise ValidationError(u"Falta canal SIAT (CUIS).")
        if not self.evento_significativo_id:
            raise ValidationError(u"Falta el tipo de evento significativo.")
        if not self.date_start or not self.date_end:
            raise ValidationError(u"Las fechas de inicio y fin son obligatorias.")
        if not self.cufd_event:
            raise ValidationError(u"Falta CUFD del evento (cufd_event).")

        # Validar duración del evento (ajusta si tu regla es 24h o 72h)
        start_dt = fields.Datetime.from_string(self.date_start)
        end_dt = fields.Datetime.from_string(self.date_end)
        if start_dt >= end_dt:
            raise ValidationError(u"La fecha de inicio debe ser anterior a la fecha fin.")
        if (end_dt - start_dt) > timedelta(hours=72):
            raise ValidationError(u"El evento no puede durar más de 72 horas.")

        # Convertir a zona horaria Bolivia (o tz usuario)
        tz_name = self.env.user.tz or 'America/La_Paz'
        tz = pytz.timezone(tz_name)

        # Odoo guarda en UTC, así que localizamos en UTC y convertimos a tz
        start_local = pytz.utc.localize(start_dt).astimezone(tz)
        end_local = pytz.utc.localize(end_dt).astimezone(tz)

        # Formato que el SIN suele aceptar con milisegundos (3 decimales)
        start_str = start_local.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
        end_str = end_local.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]

        obj_ope = self.env['siat.servicio.facturacion.operaciones']

        res = obj_ope.registro_evento_significativo(
            siat_cuis=self.siat_cuis_id.cuis,
            siat_cufd=self.siat_cuis_id.cufd_code,  # CUFD vigente del canal (para autenticación)
            branch_code=self.branch_code or self.siat_cuis_id.branch_code,
            cufd_code=self.cufd_event,  # CUFD del evento (cufdEvento)
            selling_point_code=self.selling_point_code or self.siat_cuis_id.selling_point_code,
            event_date_start=start_str,
            event_date_end=end_str,
            description=self.descripcion or self.evento_significativo_id.descripcion or '',
            code_event=self.evento_significativo_id.codigo_clasificador
        )

        # Normalizar respuesta dict/objeto
        if isinstance(res, dict):
            trans_ok = res.get('transaccion', False)
            codigo = res.get('codigoRecepcionEventoSignificativo')
            mensajes = res.get('mensajesList')
        else:
            trans_ok = getattr(res, 'transaccion', False)
            codigo = getattr(res, 'codigoRecepcionEventoSignificativo', None)
            mensajes = getattr(res, 'mensajesList', None)

        if trans_ok and codigo:
            self.write({
                'state': 'send',
                'reception_code': str(codigo),
            })
            return True

        # Si falla, levantar error con mensaje del SIN
        self.write({'state': 'failed'})

        msg = u"Error registrando evento significativo."
        if isinstance(mensajes, list) and mensajes:
            first = mensajes[0]
            if isinstance(first, dict):
                msg = first.get('descripcion', msg)
            else:
                msg = getattr(first, 'descripcion', msg)

        raise ValidationError(msg)