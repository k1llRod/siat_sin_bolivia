# -*- coding: utf-8 -*-
import math
#from odoo.modules import get_module_resource
import hashlib, zlib
import binascii
import base64
import contextlib
import cStringIO
import tarfile
import tempfile
import gzip
import os
from os.path import join
import xml.etree.ElementTree as ET
from lxml import etree
from StringIO import StringIO
import io
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from socket import gethostbyname, create_connection, error
import pytz
import socket
from dateutil import parser
import requests
from requests.exceptions import RequestException
import logging
from io import BytesIO

_logger = logging.getLogger(__name__)
# from odoo.exceptions import UserError


def action_validation_file_xml_xsd(file_xml, file_xsd):
    '''
    Funcion para validar un archivo XML con su respectivo XSD
    :param file_xml: Archivo XML de tipo Binario
    :param file_xsd: Archivo XSD de tipo Binario
    :return: Se retornara una afirmacion en caso de coincidir los archivos
    '''
    xmlschema_doc = etree.parse(StringIO(base64.decodestring(file_xsd)))
    xmlschema = etree.XMLSchema(xmlschema_doc)
    xml_doc = etree.XML(base64.decodestring(file_xml))
    result = xmlschema.validate(xml_doc)
    return result


def generate_file_gzip(file, file_name):
    '''
    Funcion para comprimir un archivo en un gzip
    :param file: archivo de tipo binario
    :param file_name: nombre del archivo gzip generado
    :return: devuelve un archivo en gzip en memoria,
    para guardarlo en un campo binaryo usar "base64.encodestring(buf.getvalue())"
    para que se descargue correctamente se le debe asignar un nombre file.gz en su respectivo campo name_file
    '''
    file_xml_b64 = base64.decodestring(file)
    buf = StringIO()
    gzip_obj = gzip.GzipFile(filename=file_name + '.gz', mode='wb', fileobj=buf)
    gzip_obj.write(file_xml_b64)
    gzip_obj.close()
    return buf


def action_generator_file_tar(xml_files):
    """
    Recibe una lista de XMLs en base64
    y devuelve un .tar.gz también en base64 (bytes codificados).
    """
    tar_buffer = BytesIO()

    # Creamos tar.gz en memoria
    with tarfile.open(fileobj=tar_buffer, mode='w:gz') as tar:
        for idx, xml_b64 in enumerate(xml_files, 1):
            if not xml_b64:
                continue

            xml_bytes = base64.b64decode(xml_b64)
            info = tarfile.TarInfo(name='%s.xml' % idx)
            info.size = len(xml_bytes)

            # El segundo argumento tiene que ser un fichero-like en bytes
            tar.addfile(info, BytesIO(xml_bytes))

    # Devolvemos el tar.gz completo en base64
    tar_buffer.seek(0)
    return base64.b64encode(tar_buffer.getvalue())

    # buf = io.BytesIO()

    # with contextlib.closing(cStringIO.StringIO()) as buf:
    #     tar = tarfile.open(fileobj=buf, mode="w:")
    #     for file in files:
    #         tmpmoddir = join(tmpdir, mod, 'i18n')
    #         os.makedirs(tmpmoddir)
    #         pofilename = ''
    #         buf = file(join(tmpmoddir, pofilename), 'w')
    #         # _process('po', [mod], modrows, buf, lang)
    #         buf.close()
    #         file_xml_b64 = base64.decodestring(file)
    #         info = tarfile.TarInfo('logo.png')
    #         info.size = len(file_xml_b64)
    #     tar.addfile(tmpdir, fileobj=None)
    #     tar.close()
    # return buf


def action_generate_file_xml(dict_xml, file_xsd):
    '''
    Funcion para crear un archivo xml binario, este sera validado con un archivo xsd
    que ingresara como parametro
    :param dict_xml: diccionario con la infromacion para generar el xml
    :param file_xsd: archivo xsd de tipo binario para validar, el xml antes de ser enviado
    :return: archivo XML de tipo binario

    EJEMPLO: de como de la estructura del dicionario esperado
    dict_xml = {'name': 'facturaComputarizadaCompraVenta',
                'name_xsd': 'facturaComputarizadaCompraVenta.xsd',
                'cabecera': [{'name': 'nitEmisor', 'value': '1003579028'},
                             {'name': 'razonSocialEmisor', 'value': 'Carlos Loza'},
                             {'name': 'codigoPuntoVenta', 'value': None}],
                'detalle': [[{'name': 'actividadEconomica', 'value': '451010'},
                             {'name': 'codigoProductoSin', 'value': '49111'},
                             {'name': 'codigoProducto', 'value': 'JN-131231'}],

                            [{'name': 'actividadEconomica', 'value': '451010'},
                             {'name': 'codigoProductoSin', 'value': '49111'},
                             {'name': 'codigoProducto', 'value': 'JN-131231'}]]
                }
    '''
    NS_XSI = "{http://www.w3.org/2001/XMLSchema-instance}"
    root = ET.Element(dict_xml['name'])
    root.set(NS_XSI + "noNamespaceSchemaLocation", dict_xml['name_xsd'])
    if dict_xml['cabecera']:
        doc = ET.SubElement(root, 'cabecera')
        for line in dict_xml['cabecera']:
            if line['value'] != None:
                ET.SubElement(doc, line['name']).text = line['value']
            else:
                ET.SubElement(doc, line['name'], {'xsi:nil': "true"})
    if dict_xml['detalle']:
        for array_line in dict_xml['detalle']:
            doc = ET.SubElement(root, 'detalle')
            for line in array_line:
                if line['value'] != None:
                    ET.SubElement(doc, line['name']).text = line['value']
                else:
                    ET.SubElement(doc, line['name'], {'xsi:nil': "true"})
    xml = ET.tostring(root, encoding='UTF-8', method='xml')
    archive_xml = xml.replace("'UTF-8\'", "'UTF-8\' standalone=\'yes\'")
    file_xml = base64.encodestring(archive_xml)
    validation = action_validation_file_xml_xsd(file_xml, file_xsd)
    if validation == False:
        raise UserError('La validacion con el archivo XSD a fallado')
        # return False
    return file_xml


def action_generator_hash(file, algorithm):
    '''
    Funcion para generar un HASH de un archivo que este guardado o este en memoria
    :param file: archivo de tipo BINARY
    :param algorithm: un texto indicando el tipo de HASH que se desea obtener['hash_256','hash_md5','hash_crc32']
    :return: El hash obtenido, una cadena de texto
    '''
    file_decode = base64.decodestring(file)
    if algorithm == 'hash_256':
        res = hashlib.sha256(file_decode).hexdigest()
    if algorithm == 'hash_md5':
        res = hashlib.md5(file_decode).hexdigest()
    if algorithm == 'hash_crc32':
        res = "%08X" % (binascii.crc32(file_decode) & 0xFFFFFFFF)
    return res


def calc_mod11(cadena):
    """metodo para obtener digito validador con modulo 11"""
    # validamos que la cadena exista
    if not cadena:
        raise Exception("String value error to calculate mod 11")
    numdig = 1
    limmult = 9
    x10 = False
    if not x10:
        numdig = 1
    for n in range(1, numdig+1):
        suma = 0
        mult = 2
        # iteramos la cadena multiplicando el factor (mult) para luego sumar
        # en esta linea basicamente se da la vuelta la cadena y generamos los factores de cada posicion
        # en base a la longitus de la cadena
        for i in range(len(cadena)-1, -1, -1):
            suma = suma + (mult * int(cadena[i]))
            mult += 1
            if mult > limmult:
                mult = 2
        if x10:
            dig = ((suma * 10) % 11) % 10
        else:
            dig = suma % 11
        if dig == 10:
            cadena += "1"
        elif dig == 11:
            cadena += "0"
        elif dig < 10:
            cadena += str(dig)
    res = cadena[len(cadena)-1]
    return res


def mod11_generator(pcadena):
    # pcadena = "00001234567892019011316372123100001110100000000010000"
    # vdigito = _calc_digit_mod11(pcadena, 1, 9, False)

    # mod11.calc_check_digit("18392825")
    # print(vdigito)
    vdigito = calc_mod11(pcadena)
    return vdigito


def _complete_cero(value, pmaxchar, prigth=False):
    """ Metodo que completa cada campo según la longitud definida con ceros a la izquierda
      de la Generación del Código Único de Factura CUF
      https://siatinfo.impuestos.gob.bo/index.php/facturacion-en-linea/algoritmos-utilizados/generacion-cuf"""
    pstring = str(value)
    return pstring.zfill(pmaxchar)

    # vnewstring = pstring
    # if pstring.Length < pmaxchar:
    #     i = pstring.Length
    #     while i < pmaxchar:
    #         # string.Concat("0", vnewstring)
    #         vnewstring = "0" + vnewstring
    #         i += 1
    #
    # return vnewstring


def _base16(pstring):
    """ La cadena resultante del modulo11 es codificada en base 16 """
    # BigInteger.Parse(p_string)
    # vvalor = pstring
    vvalor = int(pstring)
    vvalor = hex(vvalor)

    return str(vvalor).lstrip("0x").rstrip("L").upper()


def concatenate_with_cufd(pstring):
    """ La cadena resultante del modulo 11 debe ser codificada utilizando para ello Base 16 dando como resultado
        una cadena a la cual se deberá concatenar el código verificador cufd."""
    cufd = 'A19E23EF34124CD'
    return _base16(pstring) + cufd


# hacer de acuerdo a la pagina armalo correctamente
def cuf_generator(cufdcc, dic):
    # cufdcc = 'A19E23EF34124CD'
    # dic = {'nit': '5035365013',
    #        'date_time': '20211019185249155',
    #        'sucursal': '0',
    #        'modalidad': '1',
    #        'tipo_emision': '2',
    #        'tipo_factura': '1',
    #        'tipo_documento_sector': '14',
    #        'num_factura': '99999741',
    #        'punto_venta': '0'}
    strcuf = parse_concatenate(dic)
    strcuf = strcuf + mod11_generator(pcadena=strcuf)
    strcuf = _base16(strcuf)
    if strcuf:
        return strcuf + cufdcc
    else:
        raise UserWarning('"Revise el valor de strcuf"')


def format_sin_date_to_cuf(strdate):
    # 20220321142739 tamaño 17 caracteres
    dt = datetime.strptime(strdate, "%Y-%m-%dT%H:%M:%S.%f")

    return dt.strftime("%Y%m%d%H%M%S%f")[:-3]


def parse_concatenate(dic):
    strcuf = _complete_cero(dic['nit'], 13) if 'nit' in dic and dic['nit'] else ValueError('NIT value error')
    strcuf = strcuf + _complete_cero(dic['date_time'], 17) if 'date_time' in dic and dic['date_time'] else ValueError('Date value error')
    strcuf = strcuf + _complete_cero(dic['sucursal'], 4) if 'sucursal' in dic and dic['sucursal'] else ValueError('Sucursal value error')
    strcuf = strcuf + _complete_cero(dic['modalidad'], 1) if 'modalidad' in dic and dic['modalidad'] else ValueError('Modalidad value error')
    strcuf = strcuf + _complete_cero(dic['tipo_emision'], 1) if 'tipo_emision' in dic and dic['tipo_emision'] else ValueError('Tipo emision value error')
    strcuf = strcuf + _complete_cero(dic['tipo_factura'], 1) if 'tipo_factura' in dic and dic['tipo_factura'] else ValueError('Tipo factura value error')
    strcuf = strcuf + _complete_cero(dic['tipo_documento_sector'], 2) if 'tipo_documento_sector' in dic and dic['tipo_documento_sector'] else ValueError('Documento sector value error')
    strcuf = strcuf + _complete_cero(dic['num_factura'], 10) if 'num_factura' in dic and dic['num_factura'] else ValueError('Num Factura value error')
    strcuf = strcuf + _complete_cero(dic['punto_venta'], 4) if 'punto_venta' in dic and dic['punto_venta'] else ValueError('Punto de venta value error')

    return strcuf
# funcion para ver si exciste internet o no
def check_conection_internet(timeout_seconds=300):
    hosts = ["www.google.com", "8.8.8.8"]  # Alternativas: DNS de Google (8.8.8.8) y dominio
    for host in hosts:
        try:
            # Intenta conectar al host (resuelve DNS y verifica conexión)
            socket.create_connection((host, 80), timeout=timeout_seconds)
            return True
        except socket.gaierror as e:
            # Error específico de resolución DNS
            _logger.warning("Error de DNS en %s: %s", host, e)
        except (socket.error, socket.timeout) as e:
            # Otros errores de red/timeout
            _logger.warning("Error de conexión en %s: %s", host, e)
        except Exception as e:
            # Errores inesperados (registra pero continúa)
            _logger.error("Error inesperado en %s: %s", host, e)
    return False  # Todos los intentos fallaron
        
def check_connection_siat(wsdl_url):
    try:
        response = requests.get(wsdl_url, timeout=3)
        return response.status_code == 200
    except requests.RequestException:
        return False

#                   INICIO -->  metodos de tratamiento de fecha


def string_validation(strdt):
    """
    validamos que dt sea de tipo datetime
    """
    if not isinstance(strdt, str):
        raise ValidationError("El dato ingresado no es de tipo cadena")


def dt_type_validation(dt):
    """
    validamos que dt sea de tipo datetime
    """
    if not isinstance(dt, datetime):
        raise ValidationError("El dato ingresado no es de tipo datetime")


def tz_validation(dt):
    """
    validamos que el dt no tenga timezone
    """
    if dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None:
        raise ValidationError("La fecha ya contiene timezone")


def convert_strdt_to_datetime(strdt, tzformat="%Y-%m-%d %H:%M:%S"):
    """
    metodo para convertir un string_datetime a un datetime
    ***
    si se requiere podemos enviar un formato especifico, pero como formato por defecto usamos '%Y-%m-%d %H:%M:%S'
    """
    return datetime.strptime(strdt, tzformat)


def convert_dt_tz_to_custom_tz(dt, tz):
    """metodo para convertir un dt con tz UTC a un tz diferente
    parametros de entrada:
    dt = dato de tipo datetime con timezone
    tz = objeto timezone instanciadmo mediate pytz
    """
    # validamos que dt sea de tipo datetime
    dt_type_validation(dt)
    return dt.astimezone(tz)


def convert_dt_tz_to_utc_tz(dt):
    """metodo para convertir un dt con tz UTC a un tz UTC
    parametros de entrada:
    dt = dato de tipo datetime con timezone
    """
    return convert_dt_tz_to_custom_tz(dt, pytz.utc)


def add_utc_tz_to_dt(dt):
    """metodo para añadir un tz UTC a un dt sin tz"""
    # validamos que dt sea de tipo datetime
    dt_type_validation(dt)
    tz_validation(dt)
    return pytz.utc.localize(dt, is_dst=None)


def strdt_utc_to_dt_usr_tz(strdt, usertz):
    """
    metodo para convertir un string_datetime a un datetime con tz del usuario
    input:
    usertz: self.env.user.tz
    """
    # validamos que strdt sea de tipo string
    string_validation(strdt)
    # convertimos el string a datetime
    dt = convert_strdt_to_datetime(strdt)
    # obtenemos el tz del usuario
    local_tz = pytz.timezone(usertz) if usertz else pytz.utc
    # devolvemos el dt en UTC al tz del usuario
    return convert_dt_tz_to_custom_tz(add_utc_tz_to_dt(dt), local_tz)


def add_user_tz_to_dt(dt, usertz):
    """metodo para añadir un tz del usuario a un dt sin tz
    input:
    usertz: self.env.user.tz
    """
    # validamos que dt sea de tipo datetime
    dt_type_validation(dt)
    tz_validation(dt)
    local_tz = pytz.timezone(usertz) if usertz else pytz.utc
    return local_tz.localize(dt, is_dst=None)


def iso_strdt_to_dt_odoo(strdt):
    """metodo para convertirr un string_dt_ISO 'yyyy-MM-dd'T'HH:mm:ss.SSSXXX' a dt"""
    return parser.parse(strdt)


def iso_strdt_to_dt_odoo_utc(strdtiso, usertz):
    dt = iso_strdt_to_dt_odoo(strdtiso)
    local_tz = pytz.timezone(usertz) if usertz else pytz.utc
    return convert_dt_tz_to_custom_tz(local_tz.localize(dt, is_dst=None), pytz.utc)

#        FIN                   metodos de tratamiento de fechas




# print(cuf_generator())

# def algoritmoHash(self, pArchivo, algorithm):
#     hashValue = ""
#     try:
#         messageDigest = java.security.MessageDigest.getInstance(algorithm)
#         messageDigest.update(pArchivo)
#         digestedBytes = messageDigest.digest()
#         hashValue = javax.xml.bind.DatatypeConverter.printHexBinary(digestedBytes).toLowerCase()
#
#     except Exception as e:
#
#         print("Error generando Hash")
#
#     return hashValue
#
#
# def calCrc32(self, data):
#
#     checksum = java.util.zip.CRC32()
#     checksum.update(data, 0, len(data))
#     checksumValue = checksum.getValue()
#     hex = Long.toHexString(checksumValue).toUpperCase()
#
#     while len(hex) < 8:
#
#         hex = "0" + hex
#
#     return hex
