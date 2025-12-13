# -*- coding: utf-8 -*-

from openerp import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    siat_evento_significativo_id = fields.Many2one('siat.eventos.significativos')

    @api.multi
    def action_invoice_open(self):
        res = super(AccountInvoice, self).action_invoice_open()
        if len(self.invoice_line_ids.mapped('siat_giftcard_ids')) > 0:
            self.invoice_line_ids.mapped('siat_giftcard_ids').action_sell_gift_card()
        return res


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    siat_giftcard_ids = fields.One2many('siat.giftcard', 'invoice_line_id', string="Codigo Giftcard")
    gift_card = fields.Boolean(string="Gift Card", related='product_id.gift_card')

    def action_register_gift_card(self):
        if self.gift_card == True and self.invoice_id.state == 'draft':
            return {
                'name': "Asignacion de Gift Card",
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'new',
                'views': [(self.env.ref('siat_sin_bolivia.register_gift_card_form_view').id, 'form')],
                'res_model': 'register.gift.card',
                'context': {'default_invoice_line_id': self.id},
                'type': 'ir.actions.act_window',
            }
        else:
            return True
