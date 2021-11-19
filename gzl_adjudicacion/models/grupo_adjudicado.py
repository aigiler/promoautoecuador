# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class GrupoAdjudicado(models.Model):
    _name = 'grupo.adjudicado'
    _description = 'Grupo Adjudicado'
  
    name=fields.Char('Nombre',  required=True)
    codigo = fields.Char(string='Código')
    descripcion=fields.Text('Descripcion', required=True)
    active=fields.Boolean(default=True, string='Activo')
    integrantes = fields.One2many('integrante.grupo.adjudicado','grupo_id')
    monto_grupo = fields.Float(String="Cartera del grupo", compute="compute_monto_cartera")
    asamblea_id = fields.Many2one('asamblea')
    estado = fields.Selection(selection=[
            ('en_conformacion', 'En Conformación'),
            ('cerrado', 'Cerrado')
            ], string='Estado', copy=False, tracking=True, default='en_conformacion')
    cantidad_integrantes = fields.Integer(string='Cantidad de Integrantes')
    maximo_integrantes = fields.Integer(string='Máximo de Integrantes')

    
    @api.depends('integrantes.monto')
    def compute_monto_cartera(self):
        monto=0
        num_integrantes=0
        for l in self.integrantes:
            monto += l.monto
            num_integrantes +=1
            if num_integrantes > self.maximo_integrantes:
                raise ValidationError('Ha excedido el máximo de integrantes')
        self.monto_grupo=monto
        self.cantidad_integrantes=num_integrantes
   

class IntegrantesGrupo(models.Model):
    _name = 'integrante.grupo.adjudicado'
    _description = 'Integrantes de Grupo Adjudicado'
  
    descripcion=fields.Char('Descripcion',  )
    grupo_id = fields.Many2one('grupo.adjudicado')
    monto=fields.Float('Monto')
    nro_cuota_licitar = fields.Integer(string='Nro de Cuotas a Licitar')
    carta_licitacion = fields.Selection([('si', 'Si'), ('no', 'No')], string='Carta Licitación')
    codigo_integrante = fields.Char(string='Código')
    codigo_cliente = fields.Char(string='Código Cliente', related='adjudicado_id.codigo_cliente')
    vat = fields.Char(string='No. Identificación', related='adjudicado_id.vat')
    adjudicado_id = fields.Many2one('res.partner', string="Nombre", domain="[('tipo','=','adjudicado')]")
    mobile = fields.Char(string='Móvil', related='adjudicado_id.mobile')
    contrato_id = fields.Many2one('contrato', string='Contrato')
    cupo = fields.Selection(selection=[
            ('ocupado', 'Ocupado'),
            ('desocupado', 'Desocupado')
            ], string='Cupo', default='ocupado')


    @api.model
    def create(self, vals):
        grupo = self.env['grupo.adjudicado'].search([('id','=',vals['grupo_id'] )])
        existe_secuencia = self.env['ir.sequence'].search([('code','=',grupo.codigo)])
        if existe_secuencia:
            vals['codigo_integrante'] = existe_secuencia.sudo().next_by_id()
        else:
            seq = self.env['ir.sequence'].create({
                'name': 'Secuencia Grupo Adjudicado '+ grupo.codigo ,
                'implementation': 'no_gap',
                'prefix': grupo.codigo +' - ',
                'number_increment': 1,
                'code': grupo.codigo
            })
            vals['codigo_integrante'] = seq.next_by_id()
        return super(IntegrantesGrupo, self).create(vals)