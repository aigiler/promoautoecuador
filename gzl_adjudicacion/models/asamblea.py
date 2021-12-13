# -*- coding: utf-8 -*-
from odoo import api, fields, models


class Asamblea(models.Model):
    _name = 'asamblea'
    _description = 'Proceso de Asamblea'
    _rec_name = 'secuencia'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    secuencia = fields.Char(index=True)
    descripcion = fields.Text('Descripcion',  required=True,track_visibility='onchange')
    active = fields.Boolean(default=True,track_visibility='onchange')
    integrantes = fields.One2many(
        'integrante.grupo.adjudicado.asamblea', 'asamblea_id',track_visibility='onchange')
    # integrantes = fields.Many2many('integrante.grupo.adjudicado')

    junta = fields.One2many('junta.grupo.asamblea', 'asamblea_id',track_visibility='onchange')
    ganadores = fields.One2many('junta.grupo.asamblea', 'asamblea_id',track_visibility='onchange')
    fecha_inicio = fields.Datetime(String='Fecha Inicio',track_visibility='onchange')
    fecha_fin = fields.Datetime(String='Fecha Fin',track_visibility='onchange')
    tipo_asamblea = fields.Many2one(
        'tipo.contrato.adjudicado', string='Tipo de Asamblea',track_visibility='onchange')
    state = fields.Selection(selection=[
            ('borrador', 'Borrador'),
            ('en_curso', 'En Curso'),
            ('pre_cierre', 'Pre cierre'),
            ('cerrado', 'Cerrado')
            ], string='Estado', copy=False, tracking=True, default='en_curso',track_visibility='onchange')

    @api.model
    def create(self, vals):
        vals['secuencia'] = self.env['ir.sequence'].next_by_code('asamblea')
        res = self.env['res.config.settings'].sudo(1).search([], limit=1, order="id desc")
        return super(Asamblea, self).create(vals)

    @api.constrains('secuencia')
    def constrains_valor_por_defecto(self): 
        res = self.env['res.config.settings'].sudo(1).search([], limit=1, order="id desc")


    def cambio_estado_boton_borrador(self):
        return self.write({"state": "en_curso"})

    def cambio_estado_boton_en_curso(self):
        self.write({"state": "pre_cierre"})
        if self.tipo_asamblea.id==self.env.ref('gzl_adjudicacion.tipo_contrato1').id:
            listaGanadores=[]
            for grupo in self.integrantes:
                for integrante in grupo.integrantes_g:
                    dct={}
                    dct['adjudicado_id']=integrante.adjudicado_id.id
                    dct['grupo_id']=integrante.adjudicado_id.contrato.grupo.id
                    dct['nro_cuota_licitar']=integrante.nro_cuota_licitar
                    listaGanadores.append(dct)


            # This changes the list a

            # This returns a new list (a is not modified)
            listaGanadores=sorted(listaGanadores, key=lambda k : k['numeroCuota'],reverse=True) 
            self.ganadores = [(6, 0, listaGanadores[:4])]

        else:
            listaGanadores=[]
            for grupo in self.integrantes:
                for integrante in grupo.integrantes_g:
                    dct={}
                    dct['adjudicado_id']=integrante.adjudicado_id.id
                    dct['grupo_id']=integrante.adjudicado_id.contrato.grupo.id
                    dct['nro_cuota_licitar']=integrante.nro_cuota_licitar
                    listaGanadores.append(dct)


            # This changes the list a

            # This returns a new list (a is not modified)
            listaGanadores=sorted(listaGanadores, key=lambda k : k['calificacion'],reverse=True) 
            self.ganadores = [(6, 0, listaGanadores[:4])]









    def cambio_estado_boton_pre_cierre(self):
        return self.write({"state": "cerrado"})

    def cambio_estado_boton_cerrado(self):
        return self.write({"state": "cerrado"})



class GrupoAsamblea(models.Model):
    _name = 'integrante.grupo.adjudicado.asamblea'
    _description = 'Grupo Participante en asamblea'

    asamblea_id = fields.Many2one('asamblea')
    grupo_adjudicado_id = fields.Many2one('grupo.adjudicado')
    tipo_contrato = fields.Many2one(
        'tipo.contrato.adjudicado', string='Tipo de Asamblea',track_visibility='onchange')

    integrantes_g = fields.One2many('integrante.grupo.adjudicado.asamblea.clientes','grupo_id')




class IntegrantesGrupoAsamblea(models.Model):
    _name = 'integrante.grupo.adjudicado.asamblea.clientes'
    _description = 'Integrantes de Grupo Participante en asamblea'
  


    adjudicado_id = fields.Many2one('res.partner', string="Nombre")
    descripcion=fields.Char('Descripcion',  )
    grupo_id = fields.Many2one('integrante.grupo.adjudicado.asamblea')
    nro_cuota_licitar = fields.Integer(string='Nro de Cuotas a Licitar')
    carta_licitacion = fields.Selection([('si', 'Si'), ('no', 'No')], string='Carta Licitación')
    carta_doc = fields.Binary(string='Carta Licitación')




    dominio  = fields.Char(store=False, compute="_filtro_partner",readonly=True)

    @api.depends('grupo_id')
    def _filtro_partner(self):
        for l in self:
            integrantes=l.grupo_id.grupo_adjudicado_id.integrantes.filtered(lambda l: l.contrato_id.tipo_de_contrato==l.grupo_id.tipo_contrato.id).mapped('adjudicado_id').ids
            l.dominio=json.dumps( [('id','in',integrantes)] )




class GanadoresAsamblea(models.Model):
    _name = 'gana.grupo.adjudicado.asamblea.clientes'
    _description = 'Ganadores de la Asamblea'
  

    grupo_id = fields.Many2one('integrante.grupo.adjudicado.asamblea')
    adjudicado_id = fields.Many2one('res.partner', string="Nombre")
    grupo_adjudicado_id = fields.Many2one('grupo.adjudicado',string="Grupo")
    nro_cuota_licitar = fields.Integer(string='Nro de Cuotas a Licitar')










class JuntaGrupoAsamblea(models.Model):
    _name = 'junta.grupo.asamblea'
    _description = 'Comité que realiza la asamblea'

    asamblea_id = fields.Many2one('asamblea', string='Asamblea')
    empleado_id = fields.Many2one('hr.employee', string="Empleado")




