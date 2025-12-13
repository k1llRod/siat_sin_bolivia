# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError


class HistorialCufd (models.Model):
    _name = 'historial.cufd'
    _description = 'Historial de Cufd'

    name = fields.Many2one('siat.cuis', string='Cuis')

    cufd_code = fields.Char(string="Codigo Cufd")

    control_code = fields.Char(string="Codigo Control")

    direction = fields.Char(string="Direccion")

    effective_date = fields.Datetime(string="Fecha Vigencia")

    cuis = fields.Char(string="Codigo CUIS")

    branch_code = fields.Integer('Branch Code')

    selling_point_code = fields.Integer('Selling Point Code')

    def get_my_date_cufd(self, cuis_id, cuis, branch_code, selling_point_code, str_dt_criteria):
        """
        input:
        cuis_id, id de cuis
        cuis, codigo cuis
        branch_code, codigo de sucursal
        selling_point_code, codigo de punto de venta
        str_dt_criteria,  fecha de busqueda 'yyyy-mm-dd hh:mm:ss'
        ---
        output: ultimo modelo historial cufd creado antes o igual que la fecha ingresada str_dt_criteria
        """
        res = self.search([('name', '=', cuis_id),
                            ('cuis', '=', cuis),
                            ('branch_code', '=', branch_code),
                            ('selling_point_code', '=', selling_point_code),
                            ('create_date', '<=', str_dt_criteria)], limit=1, order="create_date desc")

        if not res:
            raise ValidationError("No es posible encontrar un CUFD para la fecha en cuestion, debera ingresar manualmente")

        return res



    


