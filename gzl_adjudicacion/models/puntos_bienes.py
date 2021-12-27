# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
import datetime
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, date
from dateutil.parser import parse


class PuntosBienes(models.Model):
    _name = 'puntos.bienes'
    _description = 'Bienes'
    _rec_name = "bienes"

    
    #items bienes
    poseeCasa = fields.Selection(selection=[
        ('si', 'SI'),
        ('no', 'NO')
    ], string='Casa', default='no')
    poseeTerreno = fields.Selection(selection=[
        ('si', 'SI'),
        ('no', 'NO')
    ], string='Terreno', default='no')
    poseeVehiculo = fields.Selection(selection=[
        ('si', 'SI'),
        ('no', 'NO')
    ], string='Vehiculo', default='no')
    poseeMotos = fields.Selection(selection=[
        ('si', 'SI'),
        ('no', 'NO')
    ], string='Motos', default='no')
    poseeMueblesEnseres = fields.Selection(selection=[
        ('si', 'SI'),
        ('no', 'NO')
    ], string='Muebles y Enseres', default='no')
    #puntos bienes
    puntosCasa = fields.Integer(compute='set_puntos_casa')
    puntosTerreno = fields.Integer(compute='set_puntos_terreno')
    puntosVehiculo = fields.Integer(compute='set_puntos_vehiculo')
    puntosMotos = fields.Integer(compute='set_puntos_motos')
    puntosMueblesEnseres = fields.Integer(compute='set_puntos_muebles')
    totalPuntosBienesAdj = fields.Integer(compute='calcular_puntos_bienes')
    
    @api.depends('poseeCasa')
    def set_puntos_casa(self):
        for rec in self:
            if rec.poseeCasa == 'si':
                rec.puntosCasa = 200
            else:
                rec.puntosCasa = 0

    @api.depends('poseeTerreno')
    def set_puntos_terreno(self):
        for rec in self:
            if rec.poseeTerreno == 'si':
                rec.puntosTerreno = 150
            else:
                rec.puntosTerreno = 0

    @api.depends('poseeVehiculo')
    def set_puntos_vehiculo(self):
        for rec in self:
            if rec.poseeVehiculo == 'si':
                rec.puntosVehiculo = 100
            else:
                rec.puntosVehiculo = 0
                
    @api.depends('poseeMotos')
    def set_puntos_motos(self):
        for rec in self:
            if rec.poseeMotos == 'si':
                rec.puntosMotos = 50
            else:
                rec.puntosMotos = 0

    @api.depends('poseeMueblesEnseres')
    def set_puntos_muebles(self):
        for rec in self:
            if rec.poseeMueblesEnseres == 'si':
                rec.puntosMueblesEnseres = 25
            else:
                rec.puntosMueblesEnseres = 0

    @api.depends('puntosCasa', 'puntosTerreno', 'puntosVehiculo', 'puntosMotos', 'puntosMueblesEnseres')
    def calcular_puntos_bienes(self):
        for rec in self:
            rec.totalPuntosBienesAdj = rec.puntosCasa + rec.puntosTerreno + \
                rec.puntosVehiculo + rec.puntosMotos + rec.puntosMueblesEnseres
