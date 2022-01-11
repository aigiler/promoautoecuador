
# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from datetime import date, timedelta,datetime
from dateutil.relativedelta import relativedelta
import xlsxwriter
from io import BytesIO
import base64
from odoo.exceptions import AccessError, UserError, ValidationError

import calendar
import datetime as tiempo
import itertools




class ReporteEstadoDeCuenta(models.TransientModel):
    _name = "reporte.estado.de.cuenta"
    #_inherit = ""


    def obtener_listado_partner_payment(self,filtro):
        

        if self.tipo_empresa=='proveedor':
            filtro.append(('partner_type','=','supplier'))            
        else:
            filtro.append(('partner_type','=','customer'))      

        if len(self.partner_ids.mapped("id"))!=0:
            filtro.append(('partner_id','in',self.partner_ids.mapped("id")))
        

#######filtro de facturas
        partners=list(set(self.env['account.payment'].search(filtro).mapped('partner_id').mapped('id')))
        obj_partner=self.env['res.partner'].browse(partners)
        lista_partner=[]

        for partner in obj_partner:
            dct={}
            dct['id']=partner.id
            dct['nombre']=partner.name
            lista_partner.append(dct)



        return lista_partner



            
    def obtener_listado_payment_por_empresa(self,partner_id,filtro):
        if partner_id:
            filtro.append(('partner_id','=',partner_id))            

        if self.tipo_empresa=='proveedor':
            filtro.append(('partner_type','=','supplier'))            
        else:
            filtro.append(('partner_type','=','customer'))            

#######facturas
        payments=self.env['account.payment'].search(filtro,order='name asc')
        
        lista_facturas=[]

        for payment in payments:
            dct={}
            dct['numero_documento']=payment.name
            dct['fecha_emision']=payment.payment_date
            dct['fecha_vencimiento']=payment.date_to
##### Calculo de pagos


            dct['monto_adeudado']=payment.amount_residual
            dct['monto_aplicado']=payment.amount - payment.amount_residual
            dct['monto_anticipo']=payment.amount

            dct['observaciones']=payment.communication



            lista_facturas.append(dct)
        return lista_facturas




    def print_report_pdf(self):
        return self.env.ref('gzl_reporte.repote_anticipo_pdf_id').report_action(self)


    def obtenerDatos(self,):

        filtro=[('payment_date','>=',self.date_from),
            ('payment_date','<=',self.date_to),('tipo_transaccion','=','Anticipo')]


        lista_partner=self.obtener_listado_partner_payment(filtro)
        lines=[]
        

        for partner in lista_partner:
            filtro=[('payment_date','>=',self.date_from),
                ('payment_date','<=',self.date_to),('tipo_transaccion','=','Anticipo')]
            
            lines.append({'numero_documento':partner['nombre'],'reglon':'titulo'})

            lista_anticipos=self.obtener_listado_payment_por_empresa(partner['id'],filtro)
            for dct in lista_anticipos:
                dct['reglon']='detalle'
                lines.append(dct)
            dctTotal={}
            dctTotal['numero_documento']='Total '+ partner['nombre']

            dctTotal['monto_anticipo']=round(sum(map(lambda x:x['monto_anticipo'],lista_anticipos)),2)
            dctTotal['monto_aplicado']=round(sum(map(lambda x:x['monto_aplicado'],lista_anticipos)),2)
            dctTotal['monto_adeudado']=round(sum(map(lambda x:x['monto_adeudado'],lista_anticipos)),2)
            dctTotal['reglon']='total_detalle'


            lines.append(dctTotal)
        dctTotalGeneral={}
        dctTotalGeneral['numero_documento']='Total General'

        dctTotalGeneral['monto_anticipo']=round(sum(map(lambda x:x['monto_anticipo'],list(filter(lambda x: x['reglon']=='total_detalle', lines)))),2)
        dctTotalGeneral['monto_aplicado']=round(sum(map(lambda x:x['monto_aplicado'],list(filter(lambda x: x['reglon']=='total_detalle', lines)))),2)
        dctTotalGeneral['monto_adeudado']=round(sum(map(lambda x:x['monto_adeudado'],list(filter(lambda x: x['reglon']=='total_detalle', lines)))),2)
        dctTotalGeneral['reglon']='total_general'

        lines.append(dctTotalGeneral)
        lista_obj=[]
        for l in lines:
            obj_detalle=self.env['reporte.anticipo.detalle'].create(l)
            lista_obj.append(obj_detalle)

        return lista_obj



class ReporteEstadoCuentaDetalle(models.TransientModel):
    _name = "reporte.estado.de.cuenta.detalle"

    numero_documento = fields.Char('Nro. Documento')
    fecha_emision = fields.Date('Fc. Emision')
    fecha_vencimiento = fields.Date('Fc. Vencimiento')
    monto_anticipo = fields.Float('Monto Anticipo')
    monto_aplicado = fields.Float('Monto Aplicado')
    monto_adeudado = fields.Float('Monto Adeudado')
    observaciones = fields.Char('Observaciones')
    reglon = fields.Char('Reglon')

