# -*- coding: utf-8 -*-
import string
from odoo import api, fields, models, tools
from datetime import date, timedelta, datetime
from dateutil import relativedelta as rdelta 
import xlsxwriter
from io import BytesIO
import base64
from odoo.exceptions import ValidationError


# class Users(models.Model):
#     _inherit = 'res.users'

#     codigo_asesor=fields.Char("Codigo de Asesor")

class ReportGrupos(models.TransientModel):
    _name = "reporte.grupos"

    grupo=fields.Many2one('grupo.adjudicado',string="Grupo")
    date_start = fields.Date('Fecha Inicio', required=False)
    date_end = fields.Date('Fecha Corte', required=False, default = date.today())
    fecha_contrato=fields.Date("Fecha de Contrato")
    state = fields.Selection(selection=[
        ('ACTIVADO', 'ACTIVADO'),
        ('NO ACTIVADO', 'NO ACTIVADO'),
        ('ADJUDICADO ENTREGADO', 'ADJUDICADO ENTREGADO'),
        ('ADJUDICADO NO ENTREGADO', 'ADJUDICADO ENTREGADO'),
        ('FINALIZADO', 'FINALIZADO'),
    ], string='Estado', default='NO ACTIVADO', track_visibility='onchange')

    state_simplificado=fields.Selection(selection=[
        ('AL DIA', 'AL DIA'),
        ('EN MORA', 'EN MORA'),
        ('CONGELADO', 'CONGELADO'),
        ('INSCRITO', 'INSCRITO'),
        ('LIQUIDADO', 'LIQUIDADO'),
        ('DESISTIDO PAGADO', 'DESISTIDO PAGADO'),
        ('DESISTIDO NO PAGADO', 'DESISTIDO NO PAGADO'),
    ], string='Detalle de estado', track_visibility='onchange')


    estado_deuda=fields.Selection(selection=[('todos', 'Todos'),
                                            ('al_dia', 'Al día'),
                                            ('en_mora', 'En Mora')],required=True)
    jefe_zona=fields.Selection(selection=[('j_uno', 'JEFE DE ZONA 1'),
                                            ('j_dos', 'JEFE DE ZONA 2'),
                                            ('j_tres', 'JEFE DE ZONA 3')])
    supervisor=fields.Many2one('res.users',string="Supervisor",track_visibility='onchange' )
    tipo_de_contrato = fields.Many2one('tipo.contrato.adjudicado', string='Tipo de Contrato', track_visibility='onchange')

    def print_report_xls(self):
        today = date.today()
        file_data = BytesIO()
        workbook = xlsxwriter.Workbook(file_data)
        name = 'REPORTE DE GRUPOS '+ str(today.year)
        self.xslx_body(workbook,name)
        workbook.close()
        file_data.seek(0)
        attachment = self.env['ir.attachment'].create({
            'datas': base64.b64encode(file_data.getvalue()),
            'name': name,
            'store_fname': name,
            'type': 'binary',
        })
        url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url += "/web/content/%s?download=true" %(attachment.id)
        return{
            "type": "ir.actions.act_url",
            "url": url,
            "target": "new",
        }

    def xslx_body(self,workbook,name):
        
        formato_fecha = workbook.add_format({'align':'center','valign':'vcenter','font_size': 13,'text_wrap':True,
                                                'border':True,'bg_color':'#FFFFFF','color':'#0f0000','num_format': 'dd/mm/yy'})
        formato_numero = workbook.add_format({'align':'center','valign':'vcenter','font_size': 13,'text_wrap':True,
                                            'border':True,'bg_color':'#FFFFFF','color':'#0f0000','num_format': '#,##0.00'})
        registros_tabla= workbook.add_format({'align':'center','valign':'vcenter','font_size': 13,'text_wrap':True,
                                                'border':True,'bg_color':'#FFFFFF','color':'#0f0000'})

        bold = workbook.add_format({'bold':True,'border':True, 'bg_color':'#442484','color':'#FFFFFF'})
        bold.set_center_across()
        bold.set_font_size(14)

        bold2 = workbook.add_format({'align':'center','valign':'vcenter','bold':True,'font_size': 13, 'bg_color':'#989899',
                                    'color':'#FFFFFF','text_wrap':True,'border':True})
        bold2.set_center_across()

        sheet = workbook.add_worksheet(name)

        sheet.insert_image('A1', "any_name.png",
                           {'image_data':  BytesIO(base64.b64decode( self.env.company.imagen_excel_company)), 'x_scale': 0.9, 'y_scale': 0.8,'x_scale': 0.8,
                            'y_scale':     0.8, 'align': 'left','bg_color':'#442484'})
        
        sheet.merge_range('B1:BC1', ' ', bold)
        sheet.merge_range('A2:BC2', 'REPORTE DE GRUPOS', bold)
        contrato_object= self.env['contrato']

        query="SELECT * FROM contrato"
        if self.estado_deuda=='al_dia':
            query+=" WHERE en_mora is not True "
        elif self.estado_deuda=='en_mora':
            query+=" WHERE en_mora is True "
        else:
            query+= " WHERE (en_mora is True or en_mora is not True) "

        if self.fecha_contrato:
            query+=" and fecha_contrato='{0}' ".format(self.fecha_contrato)
        if self.tipo_de_contrato:
            query+=" and tipo_de_contrato={0} ".format(self.tipo_de_contrato.id)
        if self.grupo:
            query+=" and grupo={0} ".format(self.grupo.id)
        if self.supervisor:
            query+=" and supervisor={0} ".format(self.supervisor.id)
        if self.state:
            query+=" and state='{0}'".format(self.state)
        if self.jefe_zona:
            query+=" and descripcion_adjudicaciones='{0}' ".format(self.jefe_zona)
        if self.state_simplificado:
            query+=" and state_simplificado='{0}'".format(self.state_simplificado)

        self.env.cr.execute(query)
        contrato_ids=self.env.cr.dictfetchall()
        lista_final=[]
        anio = str(datetime.today().year)
        mes_curso = str(datetime.today().month)
        
        for contrato_id in contrato_ids:
            #####obtener los nuevos campos cuotas_canceladas_mes, capital_cancelado_mes, administrativo_cancelado_mes, iva_adm_cancelado_mes, total_cancelado_mes
            contrato=self.env['contrato'].search([('id','=',contrato_id['id'])])
            pagos_ids=self.env['account.payment'].search([('partner_id','=',contrato.cliente.id),('state','=','posted'),('payment_type','=','inbound')])
            cuotas_canceladas_mes=0
            administrativo_cancelado_mes=0
            iva_adm_cancelado_mes=0
            capital_cancelado_mes=0
            lista_facturas=[]
            for rec in pagos_ids:
                if int(rec.payment_date.month)==int(mes_curso) and int(rec.payment_date.year)==int(anio):
                    for fac in rec.reconciled_invoice_ids:
                        

                        if fac.id in lista_facturas:
                            pass
                        else:
                            lista_facturas.append(fac.id)
                            if fac.contrato_id.id==contrato.id: 
                                if fac.contrato_id.id==contrato.id and fac.contrato_estado_cuenta_ids:
                                    cuotas_canceladas_mes+=len(fac.contrato_estado_cuenta_ids)
                                    administrativo_cancelado_mes+=fac.amount_untaxed
                                    iva_adm_cancelado_mes+=(fac.amount_total-fac.amount_untaxed)
                                    capital_ids=self.env['account.move'].search([('ref','=',fac.name),('state','=','posted')])
                                    for cap in capital_ids:
                                        capital_cancelado_mes+=cap.amount_total_signed
                        
                            
            total_cancelado_mes=administrativo_cancelado_mes+iva_adm_cancelado_mes+capital_cancelado_mes
            dct={'codigo_grupo':contrato.grupo.name or '',
                    'contrato':contrato.secuencia  or '',
                    'tipo_contrato':contrato.tipo_de_contrato.name  or '',
                    'nombre_cliente':contrato.cliente.name  or '',
                    'identificacion_cliente':contrato.cliente.vat  or '',
                    'telefono':contrato.cliente.phone  or '',
                    'telefono_opcional':contrato.cliente.mobile  or '',
                    'telefono_trabajo':'',
                    'direccion_trabajo':'',
                    'referenciauno':'',
                    'referenciados':'',
                    'fecha_nacimiento':contrato.cliente.fecha_nacimiento  or '',
                    'ciudad_residencia':contrato.cliente.city  or '',
                    'sucursal':'',
                    'fecha_contrato':contrato.fecha_contrato  or '',
                    'inicio_pago':contrato.fechaInicioPago  or '',
                    'plazo':contrato.plazo_meses.numero  or '',
                    'monto':contrato.monto_financiamiento  or '',
                    'cuota_capital':contrato.cuota_capital  or 0.00,
                    'cuota_adm':contrato.cuota_adm or 0.00,
                    'monto_programo':contrato.monto_programado or 0.00,
                    'cuota_programo':contrato.cuota_pago or '',
                    'seguro':0,
                    'rastreo':0,
                    'otros':0,
                    'iva_adm':contrato.iva_administrativo or 0.00,
                    'cuota_mensual':0,
                    'tasa_adm':contrato.tasa_administrativa or 0.00,
                    'capital_pagado':0,
                    'saldo_adendum':contrato.saldo_a_favor_de_capital_por_adendum or 0.00,
                    'cuotas_consecutivas':0,
                    'cuotasAdelantadas':0,
                    'cuotas_pagadas':0,
                    'estado':contrato.state,
                    'estado_simplificado':contrato.state_simplificado,
                    'estado_deuda':'',
                    'dias_vencidos':0,
                    'meses_vencidos':0,
                    'cuotas_vencidas':0,
                    'capital_vencido':0,
                    'total_vencer':0,
                    'observacion':'',
                    'email':contrato.cliente.email or '',
                    'direccion':contrato.cliente.street or '',
                    'asesor':'',
                    'supervisor':'',
                    'jefe_zona':contrato.descripcion_adjudicaciones,
                    'cuotas_canceladas_mes':cuotas_canceladas_mes,
                    'capital_cancelado_mes':capital_cancelado_mes,
                    'administrativo_cancelado_mes':administrativo_cancelado_mes,
                    'iva_adm_cancelado_mes':iva_adm_cancelado_mes,
                    'total_cancelado_mes':total_cancelado_mes}
            hoy=date.today()
            test_date = datetime(hoy.year, hoy.month, hoy.day)
            nxt_mnth = test_date.replace(day=28) + timedelta(days=4)
            res = nxt_mnth - timedelta(days=nxt_mnth.day)
            dct['cuota_mensual']=contrato.iva_administrativo+contrato.cuota_capital+contrato.cuota_adm
            sum_programo=round(sum(contrato.estado_de_cuenta_ids.mapped("programado")),2)-round(sum(contrato.estado_de_cuenta_ids.mapped("saldo_programado")),2)
            dct['capital_pagado'] =round(sum(contrato.estado_de_cuenta_ids.mapped("cuota_capital")),2)-round(sum(contrato.estado_de_cuenta_ids.mapped("saldo_cuota_capital")),2)+sum_programo
            dct['cuotas_consecutivas']=len(contrato.estado_de_cuenta_ids.filtered(lambda l: l.estado_pago=='pagado' and l.fecha<=res.date()))
            cuota_mensual=contrato.tabla_amortizacion.filtered(lambda l: l.fecha.year == hoy.year and l.fecha.month == hoy.month )
            if cuota_mensual:
                for cuota in cuota_mensual:
                    dct['cuota_mensual']=cuota_mensual.cuota_capital+cuota_mensual.cuota_adm+cuota_mensual.iva_adm+cuota_mensual.seguro+cuota_mensual.rastreo+cuota_mensual.otro

            dct['cuotasAdelantadas']=len(contrato.estado_de_cuenta_ids.filtered(lambda l: l.estado_pago=='pagado' and l.fecha>res.date()))
            dct['cuotas_pagadas']=dct['cuotas_consecutivas']+dct['cuotasAdelantadas']
            dct['capital_por_cobrar']=contrato.monto_financiamiento-dct['capital_pagado']
            dct['sum_adm_iva']=contrato.cuota_adm+contrato.iva_administrativo

            dct['administrativo_pagado']=round(sum(contrato.estado_de_cuenta_ids.mapped("cuota_adm")),2)-round(sum(contrato.estado_de_cuenta_ids.mapped("saldo_cuota_administrativa")),2)
            dct['administrativo_total']=round(sum(contrato.estado_de_cuenta_ids.mapped("cuota_adm")),2)
            dct['administrativo_por_cobrar']=dct['administrativo_total']-dct['administrativo_pagado']

            dct['iva_pagado']=round(sum(contrato.estado_de_cuenta_ids.mapped("iva_adm")),2)-round(sum(contrato.estado_de_cuenta_ids.mapped("saldo_iva")),2)
            dct['iva_total']=round(sum(contrato.estado_de_cuenta_ids.mapped("iva_adm")),2)
            dct['iva_por_cobrar']=dct['iva_total']-dct['iva_pagado']
            dct['sum_adm_iva_total']=dct['iva_total']+dct['administrativo_total']
            dct['seguro']=sum(contrato.estado_de_cuenta_ids.mapped("seguro"))
            dct['rastreo']=sum(contrato.estado_de_cuenta_ids.mapped("rastreo"))
  
            dct['otros']=sum(contrato.estado_de_cuenta_ids.mapped("otro"))
            seguro_id = self.env['wizard.actualizar.rubro'].search([('contrato_id','=',contrato.id),('rubro','=','seguro')],limit=1)
            rastreo_id = self.env['wizard.actualizar.rubro'].search([('contrato_id','=',contrato.id),('rubro','=','rastreo')],limit=1)
            otros_id = self.env['wizard.actualizar.rubro'].search([('contrato_id','=',contrato.id),('rubro','=','otro')],limit=1)
            lista_cuota=[]
            hoy=date.today()
            if contrato.en_mora:
                dct['estado_deuda']='En Mora'
                dias_vencidos=contrato.tabla_amortizacion.filtered(lambda l: l.fecha.year == hoy.year and l.fecha.month == hoy.month and l.estado_pago=='pendiente')
                for dias in dias_vencidos:
                    if hoy.day>dias.fecha.day:
                        dct['dias_vencidos']=hoy.day-dias.fecha.day
                        dct['capital_vencido']+=dias.saldo_cuota_capital
                        lista_cuota.append(dias.id)
                        dct['cuotas_vencidas']+=1
                    
                meses_vencidos=contrato.tabla_amortizacion.filtered(lambda l: l.fecha<hoy and l.id not in lista_cuota and l.estado_pago=='pendiente')
                for mes in meses_vencidos:
                    dct['meses_vencidos']+=1
                    dct['cuotas_vencidas']+=1
                    dct['capital_vencido']+=mes.saldo_cuota_capital
                    lista_cuota.append(mes.id)
            else:
                dct['estado_deuda']='Al dia'
            total_vencer=contrato.tabla_amortizacion.filtered(lambda l: l.id not in lista_cuota and l.estado_pago=='pendiente' and l.fecha>hoy)
            for total in total_vencer:
                dct['total_vencer']+=total.saldo_cuota_capital

            
            crm_id = self.env['crm.lead'].search([('contrato_id','=',contrato.id)],limit=1)
            if crm_id:
                dct['sucursal']=crm_id.surcursal_id.name
                dct['asesor']=crm_id.cerrador.name
                dct['supervisor']=crm_id.team_id.user_id.name
            if contrato.cliente:
                for contacto in contrato.cliente.child_ids:
                    if not referenciauno:
                        dct['referenciauno']=contacto.name
                    elif not referenciados:
                        dct['referenciados']=contacto.name
            lista_final.append(dct)


  



        sheet.set_column('A:A', 10)
        sheet.set_column('B:B', 10)
        sheet.set_column('C:C', 10)
        sheet.set_column('D:D', 30)
        sheet.set_column('E:E', 15)
        sheet.set_column('F:F', 15)
        sheet.set_column('G:G', 15)
        sheet.set_column('H:H', 15)
        sheet.set_column('I:I', 20)
        sheet.set_column('J:J', 25)
        sheet.set_column('K:K', 25)
        sheet.set_column('L:L', 15)
        sheet.set_column('M:M', 13)
        sheet.set_column('N:N', 13)
        sheet.set_column('O:O', 10)
        sheet.set_column('P:P', 10)
        sheet.set_column('Q:Q', 10)
        sheet.set_column('R:R', 14)
        sheet.set_column('S:S', 10)
        sheet.set_column('T:T', 10)
        sheet.set_column('U:U', 13)
        sheet.set_column('V:V', 10)
        sheet.set_column('W:W', 10)
        sheet.set_column('X:X', 10)
        sheet.set_column('Y:Y', 10)
        sheet.set_column('Z:Z', 10)
        sheet.set_column('AA:AA', 11)
        sheet.set_column('AB:AB', 10)
        sheet.set_column('AC:AC', 15)
        sheet.set_column('AD:AD', 15)
        sheet.set_column('AE:AE', 10)
        sheet.set_column('AF:AF', 10)
        sheet.set_column('AG:AG', 10)
        sheet.set_column('AH:AH', 10)
        sheet.set_column('AI:AI', 10)
        sheet.set_column('AJ:AJ', 10)
        sheet.set_column('AK:AK', 10)
        sheet.set_column('AL:AL', 10)
        sheet.set_column('AM:AM', 14)
        sheet.set_column('AN:AN', 14)
        sheet.set_column('AO:AO', 20)
        sheet.set_column('AP:AP', 20)
        sheet.set_column('AQ:AQ', 20)
        sheet.set_column('AR:AR', 25)
        sheet.set_column('AS:AS', 25)
        sheet.set_column('AT:AT', 25)
        sheet.set_column('AU:AU', 25)
        sheet.set_column('AV:AV', 25)
        sheet.set_column('AW:AW', 25)
        sheet.set_column('AX:AX', 25)
        sheet.set_column('AY:AY', 25)
        sheet.set_column('AZ:AZ', 25)



        sheet.write(4, 0, 'Cod. Grupo', bold2)
        sheet.write(4, 1, 'Contrato', bold2)
        sheet.write(4, 2, 'Tipo', bold2)
        sheet.write(4, 3, 'Cliente No.', bold2)
        sheet.write(4, 4, 'Identificación', bold2)
        sheet.write(4, 5, 'Teléfono', bold2)
        sheet.write(4, 6, 'TELEFONO OPCIONAL', bold2)
        sheet.write(4, 7, 'TELEFONO DE TRABAJO', bold2)
        sheet.write(4, 8, 'DIRECCION DE TRABAJO', bold2)
        sheet.write(4, 9, 'REFERENCIA PERSONAL 1', bold2)
        sheet.write(4, 10, 'REFERENCIA PERSONAL 2', bold2)
        sheet.write(4, 11, 'FECHA DE NACIMIENTO', bold2)
        sheet.write(4, 12, 'CIUDAD RESIDENCIA', bold2)
        sheet.write(4, 13, 'AGENCIA', bold2)
        sheet.write(4, 14, 'FECHA DE iNSCRIPCIÓN', bold2)
        sheet.write(4, 15, 'Inicio Pago', bold2)
        sheet.write(4, 16, 'Plazo', bold2)
        sheet.write(4, 17, 'Monto', bold2)
        sheet.write(4, 18, 'Cuota Capital', bold2)
        sheet.write(4, 19, 'Cuota Adm', bold2)
        sheet.write(4, 20, 'Monto Program.', bold2)
        sheet.write(4, 21, 'Cuota Program.', bold2)
        sheet.write(4, 22, 'SEGURO', bold2)
        sheet.write(4, 23, 'RASTREO', bold2)
        sheet.write(4, 24, 'OTROS', bold2)
        sheet.write(4, 25, 'IVA Adm.', bold2)
        sheet.write(4, 26, 'CUOTA MENSUAL', bold2)
        sheet.write(4, 27, 'Tasa Adm.', bold2)
        sheet.write(4, 28, 'Capital Pagado', bold2)
        sheet.write(4, 29, 'Saldo a favor de capital por adendum', bold2)
        sheet.write(4, 30, 'Cant. Cuotas consecutivas', bold2)
        sheet.write(4, 31, 'Cant. Precancelaciones', bold2)
        sheet.write(4, 32, 'Cuotas Pagadas', bold2)
        sheet.write(4, 33, 'Estado', bold2)
        sheet.write(4, 34, 'Detalle Estado', bold2)
        sheet.write(4, 35, 'Estado deuda', bold2)
        sheet.write(4, 36, 'DIAS VENCIDOS', bold2)
        sheet.write(4, 37, 'MESES VENCIDOS', bold2)
        sheet.write(4, 38, 'N°CUOTAS VENCIDAS', bold2)
        sheet.write(4, 39, 'TOTAL VENCIDO', bold2)
        sheet.write(4, 40, 'TOTAL POR VENCER', bold2)
        sheet.write(4, 41, 'OBSERVACION', bold2)
        sheet.write(4, 42, 'Email', bold2)
        sheet.write(4, 43, 'Dirección', bold2)
        sheet.write(4, 44, 'ASESOR', bold2)
        sheet.write(4, 45, 'SUPERVISOR', bold2)
        sheet.write(4, 46, 'Jefe de Zona', bold2)
        sheet.write(4, 47, 'CAPITAL POR COBRAR', bold2)
        sheet.write(4, 48, 'CUOTA ADM + IVA ADM', bold2)
        sheet.write(4, 49, 'ADMINISTRATIVO PAGADO', bold2)
        sheet.write(4, 50, 'ADMINISTRATIVO PLAZO TOTAL', bold2)
        sheet.write(4, 51, 'ADMINISTRATIVO POR COBRAR', bold2)
        sheet.write(4, 52, 'IVA PAGADO', bold2)
        sheet.write(4, 53, 'IVA PLAZO TOTAL', bold2)
        sheet.write(4, 54, 'IVA POR COBRAR', bold2)
        sheet.write(4, 55, 'CUOTA ADM + IVA ADM TOTAL', bold2)
        sheet.write(4, 56, 'CUOTAS CANCELADAS EN EL MES', bold2)
        sheet.write(4, 57, 'CAPITAL CANCELADO EN EL MES', bold2)
        sheet.write(4, 58, 'ADMINISTRATIVO CANCELADO EN EL MES', bold2)
        sheet.write(4, 59, 'IVA CANCELADO EN EL MES', bold2)
        sheet.write(4, 60, 'TOTAL CANCELADO EN EL MES', bold2)
        row=5

        lista_asesores=[]
        
        for line in lista_final:
            sheet.write(row,0, line['codigo_grupo'], registros_tabla)
            sheet.write(row, 1, line['contrato'], registros_tabla)
            sheet.write(row, 2,line['tipo_contrato'], registros_tabla)
            sheet.write(row, 3, line['nombre_cliente'], registros_tabla)
            sheet.write(row, 4, line['identificacion_cliente'], registros_tabla)
            sheet.write(row, 5, line['telefono'], registros_tabla)
            sheet.write(row, 6,line['telefono_opcional'] , registros_tabla)
            sheet.write(row, 7, line['telefono_trabajo'], registros_tabla)
            sheet.write(row, 8, line['direccion_trabajo'], registros_tabla)
            sheet.write(row, 9, line['referenciauno'], registros_tabla)
            sheet.write(row, 10, line['referenciados'], registros_tabla)
            sheet.write(row, 11, line['fecha_nacimiento'], formato_fecha)
            sheet.write(row, 12,line['ciudad_residencia'], registros_tabla)
            sheet.write(row, 13, line['sucursal'], registros_tabla)
            sheet.write(row, 14, line['fecha_contrato'], formato_fecha)
            sheet.write(row, 15, line['inicio_pago'], formato_fecha)
            sheet.write(row, 16,line['plazo'] , registros_tabla)
            sheet.write(row, 17, line['monto'], formato_numero)
            sheet.write(row, 18, line['cuota_capital'], formato_numero)
            sheet.write(row, 19, line['cuota_adm'], formato_numero)
            sheet.write(row, 20, line['monto_programo'], formato_numero)
            sheet.write(row, 21, line['cuota_programo'], registros_tabla)
            sheet.write(row, 22,line['seguro'], formato_numero)
            sheet.write(row, 23, line['rastreo'], formato_numero)
            sheet.write(row, 24, line['otros'], formato_numero)
            sheet.write(row, 25, line['iva_adm'], formato_numero)
            sheet.write(row, 26,line['cuota_mensual'] , formato_numero)
            sheet.write(row, 27, line['tasa_adm'], formato_numero)
            sheet.write(row, 28, line['capital_pagado'], formato_numero)
            sheet.write(row, 29, line['saldo_adendum'], formato_numero)
            sheet.write(row, 30, line['cuotas_consecutivas'], registros_tabla)
            sheet.write(row, 31, line['cuotasAdelantadas'], registros_tabla)
            sheet.write(row, 32,line['cuotas_pagadas'], registros_tabla)
            sheet.write(row, 33, line['estado'], registros_tabla)
            sheet.write(row, 34, line['estado_simplificado'], registros_tabla)
            sheet.write(row, 35, line['estado_deuda'], registros_tabla)
            sheet.write(row, 36, line['dias_vencidos'], registros_tabla)
            sheet.write(row, 37,line['meses_vencidos'] , registros_tabla)
            sheet.write(row, 38, line['cuotas_vencidas'], registros_tabla)
            sheet.write(row, 39, line['capital_vencido'], formato_numero)
            sheet.write(row, 40, line['total_vencer'], formato_numero)
            sheet.write(row, 41, line['observacion'], registros_tabla)
            sheet.write(row, 42, line['email'], registros_tabla)
            sheet.write(row, 43, line['direccion'], registros_tabla)
            sheet.write(row, 44, line['asesor'], registros_tabla)
            sheet.write(row, 45, line['supervisor'], registros_tabla)
            sheet.write(row, 46, line['jefe_zona'], registros_tabla)
            sheet.write(row, 47, line['capital_por_cobrar'], formato_numero)
            sheet.write(row, 48, line['sum_adm_iva'], formato_numero)
            sheet.write(row, 49, line['administrativo_pagado'], formato_numero)
            sheet.write(row, 50, line['administrativo_total'], formato_numero)
            sheet.write(row, 51, line['administrativo_por_cobrar'], formato_numero)
            sheet.write(row, 52, line['iva_pagado'], formato_numero)
            sheet.write(row, 53, line['iva_total'], formato_numero)
            sheet.write(row, 54, line['iva_por_cobrar'], formato_numero)
            sheet.write(row, 55, line['sum_adm_iva_total'], formato_numero)
            sheet.write(row, 56, line['cuotas_canceladas_mes'], registros_tabla)
            sheet.write(row, 57, line['capital_cancelado_mes'], formato_numero)
            sheet.write(row, 58, line['administrativo_cancelado_mes'], formato_numero)
            sheet.write(row, 59, line['iva_adm_cancelado_mes'], formato_numero)
            sheet.write(row, 60, line['total_cancelado_mes'], formato_numero)


            row+=1


