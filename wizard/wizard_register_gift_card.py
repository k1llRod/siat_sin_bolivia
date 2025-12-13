# -*- coding: utf-8 -*-
from openerp import fields, api, models, _
# from openerp.exceptions import UserError


class RegisterGiftCard(models.TransientModel):
    _name = "register.gift.card"

    amount = fields.Many2one('amount.giftcard', string='Monto a buscar', required=True)
    amount_ref = fields.Monetary(string="Monto ref", related='amount.amount')
    invoice_line_id = fields.Many2one('account.invoice.line', string='Factura')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    siat_giftcard_ids = fields.Many2many('siat.giftcard', string="Giftcard", required=True)

    @api.onchange('amount')
    def _onchange_amount(self):
        self.siat_giftcard_ids = self.env['siat.giftcard']

    def action_assign_gift_card(self):
        if self.siat_giftcard_ids:
            self.invoice_line_id.update({'price_unit': self.amount.amount,
                                        'quantity': len(self.siat_giftcard_ids),
                                         })
            self.invoice_line_id.invoice_id._onchange_invoice_line_ids()
            self.invoice_line_id.update({'siat_giftcard_ids': [(6, 0, self.siat_giftcard_ids.ids)]})
