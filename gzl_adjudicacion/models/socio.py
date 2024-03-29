# -*- coding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, tools,  _
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime,timedelta,date
import re


class Partner(models.Model):   
    _inherit = 'res.partner'    
  



    monto = fields.Float(string='Monto')
    id_cliente = fields.Char(string='ID Cliente')
    direccion = fields.Text(string='Dirección')
    tipo_contrato = fields.Many2one("tipo.contrato.adjudicado", String="Tipo de Contrato")
    codigo_cliente = fields.Char(string='Código Cliente')
    fecha_nacimiento  = fields.Date(string='Fecha de nacimiento')
    estado_civil = fields.Selection(selection=[
                    ('soltero', 'Soltero/a'),
                    ('union_libre', 'Unión libre'),
                    ('casado', 'Casado/a'),
                    ('divorciado', 'Divorciado/a'),
                    ('viudo', 'Viudo/a')                    
                    ], string='Estado Civil', default='soltero')
    num_cargas_familiares = fields.Integer(string='Cargas Familiares')
    comisionFacturaConcesionario = fields.Float(string="PORCENTAJE COMISION FACTURA A NOMBRE CONCESIONARIO")
    retencion_fuente=fields.Float(string="PORCENTAJE RETENCIÓN A LA FUENTE")
    retencion_iva=fields.Float(string="PORCENTAJE RETENCIÓN IVA")

    conyuge=fields.Char(string='Nombre del Conyuge')

    fechaNacimientoConyuge = fields.Date(string='Fecha de Nacimiento Conyuge')
    vatConyuge = fields.Char(string='Cedula de Ciudadanía Conyuge')
    direccion_trabajo=fields.Char(string='Dirección Laboral')
    nombre_compania=fields.Char(string='Compañia')
    telefono_trabajo=fields.Char(string='Telefono')
    cargo=fields.Char(string='Cargo')