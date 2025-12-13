# -*- coding: utf-8 -*-

from openerp import api, fields, models
from odoo.exceptions import UserError


class account_payment(models.Model):
    _inherit = 'account.payment'

    gift_card = fields.Boolean(string="Gift Card", related="journal_id.gift_card")

    siat_giftcard_id = fields.Many2one('siat.giftcard', string="Codigo Giftcard")

    first_number_card = fields.Char(string="Datos tarjeta", size=4)

    last_number_card = fields.Char(string="Datos tarjeta", size=4)

    it_card = fields.Boolean(string="Es Tarjeta", related="journal_id.it_card")

    @api.onchange('journal_id', 'siat_giftcard_id')
    def _onchange_journal_id(self):
        if self.gift_card == True:
            if self.siat_giftcard_id:
                amount = self.siat_giftcard_id.amount.amount if self.siat_giftcard_id.amount else 0.0
                self.update({'amount': amount})
            else:
                self.update({'amount': 0.0})

    @api.multi
    def post(self):
        print('###########################  -> POST')
        for line in self:
            if line.journal_id.gift_card == True:
                line.siat_giftcard_id.validate_siat_gift_card()
        super(account_payment, self).post()

    @api.one
    @api.constrains('first_number_card', 'last_number_card')
    def constrains_number_card(self):
        if self.journal_id.it_card and (not str(self.first_number_card).isdigit() or not str(self.last_number_card).isdigit() or len(self.first_number_card) != 4 or len(self.last_number_card) != 4):
            raise UserError('La informacion de tarjetas deben ser solo numeros y grupos de 4 digitos')


class AccountJournal(models.Model):

    _inherit = "account.journal"

    gift_card = fields.Boolean(string="Gift Card")
    metodo_pago_id = fields.Many2one('tipo.metodo.pago', string='metodo de pago',)
    it_card = fields.Boolean(string="Es Tarjeta", default=False)



