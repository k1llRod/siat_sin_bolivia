# -*- coding: utf-8 -*-
{
    'name': 'SIAT Sin Bolivia',
    'version': '1.0.0',
    'author': 'Jorge Martinez, DAO SYSTEMS',
    'summary': 'Integracion SIAT V2',
    'category': 'Account',
    'description': """
INTEGRACION DE FACTURACION SIAT V2:
===================================
Este modulo esta concebido para aplicar la base de integracion de todo lo que dicta la normativa de impuestos nacionales de Bolivia
para generar facturas en base a la modalidad computarizada en linea
    """,
    'depends': ['base',
                'product',
                'payment',
                'account_accountant',
                'product_category_taxes'],
    'external_dependencies': {'python': ['suds']},
    'data': [
        'security/ir.model.access.csv',
        'data/siat_sin_bolivia_data.xml',
        'data/product_template_data.xml',
        'views/res_company_view.xml',
        'views/product_view.xml',
        'views/siat_cuis_view.xml',
        'views/siat_giftcard_view.xml',
        'views/res_config_views.xml',
        'views/account_payment_view.xml',
        'views/account_invoice_view.xml',
        'views/siat_eventos_significativos.xml',
        'views/partner_view.xml',
        'views/product_uom_views.xml',
        'views/res_currency_view.xml',
        'wizard/wizard_respuesta_view.xml',
        'wizard/wizard_register_gift_card_view.xml',
        'wizard/wizard_register_point_of_sale_view.xml',
        'wizard/wizard_cancel_invoice_siat_view.xml',
        'wizard/wizard_register_event_view.xml',

    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
