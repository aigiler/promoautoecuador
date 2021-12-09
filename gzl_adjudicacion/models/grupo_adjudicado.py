# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class GrupoAdjudicado(models.Model):
    _name = 'grupo.adjudicado'
    _description = 'Grupo Adjudicado'
    _inherit = ['mail.thread', 'mail.activity.mixin']



    name=fields.Char('Nombre',  required=True , track_visibility='onchange')
    codigo = fields.Char(string='Código',track_visibility='onchange')
    descripcion=fields.Text('Descripcion', required=True)
    active=fields.Boolean(default=True, string='Activo',track_visibility='onchange')
    integrantes = fields.One2many('integrante.grupo.adjudicado','grupo_id',track_visibility='onchange')
    monto_grupo = fields.Float(String="Cartera del grupo",default=0, compute="compute_monto_cartera",track_visibility='onchange',store=True)
    asamblea_id = fields.Many2one('asamblea')
    estado = fields.Selection(selection=[
            ('en_conformacion', 'En Conformación'),
            ('cerrado', 'Cerrado')
            ], string='Estado', copy=False, tracking=True, default='en_conformacion',track_visibility='onchange')
    cantidad_integrantes = fields.Integer(string='Cantidad de Integrantes',track_visibility='onchange')
    maximo_integrantes = fields.Integer(string='Máximo de Integrantes',track_visibility='onchange')

    _sql_constraints = [
        ('codigo_uniq', 'unique (codigo)', 'El código ya existe.')
    ]
    
    @api.depends('integrantes.monto')
    def compute_monto_cartera(self):
        num_integrantes=0
        for l in self.integrantes:
            num_integrantes +=1
            if num_integrantes > self.maximo_integrantes:
                raise ValidationError('Ha excedido el máximo de integrantes.')
        self.cantidad_integrantes=num_integrantes
   


    monto_grupo = fields.Float(string='Monto Pagado',compute="calcular_monto_pagado",store=True)


    @api.depends("integrantes")
    def calcular_monto_pagado(self,):
        for l in self:
            monto=round(sum(l.integrantes.mapped("contrato_id").mapped("monto_pagado")),2)
            l.monto_grupo=monto


    def cerrar_grupo(self,):
        self.state='cerrado'

    def abrir_grupo(self,):
        self.state='en_conformacion'


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





    @api.onchange("adjudicado_id")
    def agregar_contrato(self, ):

        if self.adjudicado_id.id:
            contrato=self.env['contrato'].search([('cliente','=',self.adjudicado_id.id)],limit=1)
            if len(contrato)>0:
                self.contrato_id=contrato.id






    @api.constrains("adjudicado_id")
    def validar_cliente_en_otro_grupo(self, ):


        if self.adjudicado_id.id:
            grupos=self.env['grupo.adjudicado'].search([('id','!=',self.grupo_id.id)])
            listaIntegrantes=[]

            for grupo in grupos:
                listaIntegrantes=listaIntegrantes + (grupo.integrantes.mapped('adjudicado_id').ids)
            listaIntegrantes=list(set(listaGrupos))

            if self.adjudicado_id.id in listaGrupos:
                raise ValidationError("El integrante {0} ya está ingresado en otro grupo".format(self.adjudicado_id.name))











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