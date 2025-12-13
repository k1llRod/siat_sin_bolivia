# -*- coding: utf-8 -*-

from odoo import fields, models, api


class AccountConfigSettings(models.TransientModel):
    """
    Extender el model account.config.settings de Account.
    Adicionar configuración para instalar el modulo siat
    """
    _inherit = 'account.config.settings'

    siat_default_payment_code = fields.Many2one('tipo.metodo.pago', string='Siat Default Payment Code',
                                                help="Establece un metodo por defecto en el caso de que un invoice no registre un pago")
    siat_monto_max_cliente_sm = fields.Float(string='Siat Monto maximo', digits=(16, 2), default=0.0,
                                             help="monto maximo para ventas sin datos del cliente")

    @api.multi
    def set_default_siat_default_payment_code(self):
        IrValues = self.env['ir.values']
        IrValues.set_default('account.config.settings', 'siat_default_payment_code', self.siat_default_payment_code.id)

    @api.multi
    def set_default_siat_monto_max_cliente_sm(self):
        IrValues = self.env['ir.values']
        IrValues.set_default('account.config.settings', 'siat_monto_max_cliente_sm', self.siat_monto_max_cliente_sm)

    @api.model
    def get_default_siat_default_payment_code(self, fields):
        return {
            'siat_default_payment_code': self.env['ir.values'].get_default('account.config.settings', 'siat_default_payment_code')
        }

    @api.model
    def get_default_siat_monto_max_cliente_sm(self, fields):
        return {
            'siat_monto_max_cliente_sm': self.env['ir.values'].get_default('account.config.settings',
                                                                           'siat_monto_max_cliente_sm')
        }
