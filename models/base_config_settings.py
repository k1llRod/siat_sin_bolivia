# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class BaseConfigSettings(models.TransientModel):
    _inherit = 'base.config.settings'

    name_siat_file_xsd = fields.Char(string="Nombre Siat file xsd", default='Siat xsd')
    siat_file_xsd = fields.Binary(string="Siat file xsd")
    siat_cetr = fields.Binary(string="Certificado ADSIB",
                              help="Carge el certificado emitido por ADSIB en formato .pk12")
    siat_pass = fields.Char(string="Contraseña",
                            help="Por lo general esta contraseña es la misma que se establece en la creacion del certificado ")
    siat_route = fields.Char(string="Ruta de archivo de firma",
                            help="Ruta en al cual se encuntra su archivo de firma digital")

    @api.multi
    def set_default_siat_file_xsd(self):
        self.env['ir.values'].set_default('base.config.settings', 'siat_file_xsd', self.siat_file_xsd)

    @api.model
    def get_default_siat_file_xsd(self, fields):
        return {'siat_file_xsd': self.env['ir.values'].get_default('base.config.settings', 'siat_file_xsd')}

    @api.multi
    def set_default_name_siat_file_xsd(self):
        self.env['ir.values'].set_default('base.config.settings', 'name_siat_file_xsd', self.name_siat_file_xsd)

    @api.model
    def get_default_name_siat_file_xsd(self, fields):
        return {'name_siat_file_xsd': self.env['ir.values'].get_default('base.config.settings', 'name_siat_file_xsd')}

    @api.multi
    def set_default_siat_cetr(self):
        self.env['ir.values'].set_default('base.config.settings', 'siat_cetr', self.siat_cetr)

    @api.model
    def get_default_siat_cetr(self, fields):
        return {'siat_cetr': self.env['ir.values'].get_default('base.config.settings', 'siat_cetr')}

    @api.multi
    def set_default_siat_pass(self):
        self.env['ir.values'].set_default('base.config.settings', 'siat_pass', self.siat_pass)

    @api.model
    def get_default_siat_pass(self, fields):
        return {'siat_pass': self.env['ir.values'].get_default('base.config.settings', 'siat_pass')}

    @api.multi
    def set_default_siat_route(self):
        self.env['ir.values'].set_default('base.config.settings', 'siat_route', self.siat_route)

    @api.model
    def get_default_siat_route(self, fields):
        return {'siat_route': self.env['ir.values'].get_default('base.config.settings', 'siat_route')}