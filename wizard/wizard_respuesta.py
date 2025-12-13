# -*- coding: utf-8 -*-
from openerp import fields, models, _
# from openerp.exceptions import UserError


class SiatWizardResp(models.TransientModel):
    """
    creamos este wizard para poder mostrar mensajes ya que al usar botones de tipo object no es posioble lanzar warnings
    """
    _name = "siat.wizard.resp"

    title = fields.Char("Titulo")
    message = fields.Char("Mensaje")
