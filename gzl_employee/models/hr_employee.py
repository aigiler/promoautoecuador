# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import *
from . import crear_contrato_doc
import shutil
import base64


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    direccion = fields.Char('Dirección')
    lugar_residencia = fields.Char('Lugar de Residencia')
    ciudad_trabajo = fields.Char('Ciudad de Trabajo')
    correo = fields.Char('Correo electrónico')
    res_bank_id = fields.Many2one('res.bank', string='Banco')
    account_type = fields.Selection(selection=[
            ('A', 'Ahorros'),
            ('C', 'Corriente'),
            ('M', 'Cuenta Amiga')], string='Tipo de Cuenta')
    number_bank = fields.Char('Número de Cta')
    children_id = fields.One2many('hr.employee.children','employee_id', string='Id hijos')
    observation = fields.Text(string='Observaciones')
    property_account_payable_id = fields.Many2one('account.account', company_dependent=True,
        string="Cuenta por Pagar",
        domain="[('internal_type', '=', 'payable'), ('deprecated', '=', False)]",
        help="This account will be used instead of the default one as the payable account for the current partner")
    property_account_receivable_id = fields.Many2one('account.account', company_dependent=True,
        string="Cuenta por Cobrar",
        domain="[('internal_type', '=', 'receivable'), ('deprecated', '=', False)]",
        help="This account will be used instead of the default one as the receivable account for the current partner")

    def has_13months(self, date_init, contract=False):
        days = sum([(c.date_end - c.date_start).days for c in self.contract_ids if c.state == 'close'])
        days = 0 if not days else days[0]
        if not contract:
            raise ValidationError("%s debe tener un contracto activo." %(self.name))
        days += (date_init - contract.date_start).days
        if days >= 395:
            return days
        elif days < 395 and days > 365:
            return days - 365
        return 0


    def job_ingreso_nomina(self):
        hoy=date.today()
        contatos_ids=self.env['hr.contract'].search([('state','=','open')])
        for x in contatos_ids:
            nominas_ids=self.env['hr.payslip'].search([('employee_id','=',x.employee_id.id)])
            nomina_mes=nominas_ids.filtered(lambda l: l.date_from.year == hoy.year and l.date_from.month == hoy.month and l.payslip_run_id.type_payroll == 'monthly')
            if len(nomina_mes)==0:
                self.envio_correos_plantilla('email_nomina_pendiente',x.employee_id.id)


    def envio_correos_plantilla(self, plantilla,id_envio):

        try:
            ir_model_data = self.env['ir.model.data']
            template_id = ir_model_data.get_object_reference('gzl_adjudicacion', plantilla)[1]
        except ValueError:
            template_id = False
#Si existe capturo el template
        if template_id:
            obj_template=self.env['mail.template'].browse(template_id)

            email_id=obj_template.send_mail(id_envio)


    def job_ingreso_comisiones(self):
        hoy=date.today()
        contatos_ids=self.env['hr.contract'].search([('state','=','open')])
        for x in contatos_ids:
            tipo_comision=self.env['hr.payslip.input.type'].search([('code','=','COMI')])
            comisiones_ids=self.env['hr.input'].search([('state','=',True),('employee_id','=',x.employee_id.id),('input_type_id','=',tipo_comision.id)])
            if comisiones_ids:
                self.envio_correos_plantilla('email_comisiones_pendientes',x.employee_id.id)

    @api.onchange("name","identification_id","birthday","estado_civil","phone","mobile_phone",
                "country_id","direccion","property_account_receivable_id","property_account_payable_id")
    def actualizar_partner(self):
        for l in self:
            if self.address_id:
                estado_civil=""
                if l.marital=="single":
                    estado_civil="soltero"
                elif l.marital=="married":
                    estado_civil="casado"
                elif l.marital=="widower":
                    estado_civil="viudo"
                elif l.marital=="divorced":
                    estado_civil="divorciado"
                elif l.marital=="free_union":
                    estado_civil="union_libre"
                nombre_conyuge=""
                nacimiento_conyuge=""
                cargas_ids=self.env['hr.employee.children'].search([('parentezco','=','conyuge')],limit=1)
                for x in cargas_ids:
                    nombre_conyuge=x.name
                    nacimiento_conyuge=x.date_birth
                dct={
                    'name':self.name,
                    'vat':self.identification_id,
                    'fecha_nacimiento':self.birthday,
                    'estado_civil':estado_civil,
                    'phone':self.phone,
                    'mobile':self.mobile_phone,
                    'country_id':self.country_id.id,
                    'street':self.direccion,
                    'direccion_trabajo':self.work_location,
                    'nombre_compania':" PROMOAUTO ECUADOR S.A.",
                    'telefono_trabajo':self.work_phone,
                    'cargo':self.job_id.name,
                    'conyuge':nombre_conyuge,
                    "fechaNacimientoConyuge":nacimiento_conyuge,
                    'property_account_receivable_id':self.property_account_receivable_id.id,
                    "property_account_payable_id":self.property_account_payable_id.id
                }
                self.address_id.write(dct)



    @api.constrains("name")
    def crear_partner(self):
        for l in self:
            estado_civil=""
            if l.marital=="single":
                estado_civil="soltero"
            elif l.marital=="married":
                estado_civil="casado"
            elif l.marital=="widower":
                estado_civil="viudo"
            elif l.marital=="divorced":
                estado_civil="divorciado"
            elif l.marital=="free_union":
                estado_civil="union_libre"
            nombre_conyuge=""
            nacimiento_conyuge=False
            cargas_ids=self.env['hr.employee.children'].search([('parentezco','=','conyuge')],limit=1)
            for x in cargas_ids:
                nombre_conyuge=x.name
                nacimiento_conyuge=x.date_birth
            dct={
                'name':self.name,
                'vat':self.identification_id,
                'fecha_nacimiento':self.birthday,
                'estado_civil':estado_civil,
                'phone':self.phone,
                'mobile':self.mobile_phone,
                'country_id':self.country_id.id,
                'street':self.direccion,
                'direccion_trabajo':self.work_location,
                'nombre_compania':" PROMOAUTO ECUADOR S.A.",
                'telefono_trabajo':self.work_phone,
                'cargo':self.job_id.name,
                'conyuge':nombre_conyuge,
                "fechaNacimientoConyuge":nacimiento_conyuge,
                'property_account_receivable_id':self.property_account_receivable_id.id,
                "property_account_payable_id":self.property_account_payable_id.id
            }
            empleado_partner_id=self.env['res.partner'].create(dct)
            self.address_id=False
            self.address_id=empleado_partner_id.id



class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'


    direccion = fields.Char('Dirección')
    correo = fields.Char('Correo electrónico')
    res_bank_id = fields.Many2one('res.bank', string='Banco')
    account_type = fields.Selection(selection=[
            ('A', 'Ahorros'),
            ('C', 'Corriente'),
            ('M', 'Cuenta Amiga')], string='Tipo de Cuenta')
    number_bank = fields.Char('Número de Cta')
    children_id = fields.One2many('hr.employee.children','employee_id', string='Id hijos')
    observation = fields.Text(string='Observaciones')






class HrEmployeeChildren(models.Model):
    _name = 'hr.employee.children'
    
    employee_id = fields.Many2one('hr.employee', string='Id empleado')
    name = fields.Char(string='Nombre')
    date_birth = fields.Date(string='Fecha de nacimiento')
    age = fields.Char(string='Edad')
    gender = fields.Selection(selection=[
            ('femenino', 'Femenino'),
            ('masculino', 'Masculino')], string='Género', required=True)
    

    parentezco = fields.Selection(selection=[
            ('hijo', 'Hj@'),
            ('conyuge', 'Conyuge')], string='Parentezco', required=True)

    @api.depends('date_birth')
    @api.onchange('date_birth')
    def calcular_edad(self):
        self.age = ''
        for rec in self:
            today = date.today()
            if rec.date_birth:
                edad = today.year - rec.date_birth.year - \
                    ((today.month, today.day) < (
                        rec.date_birth.month, rec.date_birth.day))
                rec.age = str(edad)+' años'

    def planned_action_age(self):
        res = self.env['hr.employee.children'].search([('date_birth','!=',False)])
        for l in res:
            if l.date_birth:
                now = date.today()
                #month = str(now.month - l.date_birth.month)
                #m=''
                #if month=='1':
                #    m='mes'
                #else:
                #    m='meses'
                l.age = str(now.year - l.date_birth.year) +' años ' 




class Contract(models.Model):
    _inherit = 'hr.contract'


    def convierte_cifra(self,numero,sw):
        lista_centana = ["",("CIEN","CIENTO"),"DOSCIENTOS","TRESCIENTOS","CUATROCIENTOS","QUINIENTOS","SEISCIENTOS","SETECIENTOS","OCHOCIENTOS","NOVECIENTOS"]
        lista_decena = ["",("DIEZ","ONCE","DOCE","TRECE","CATORCE","QUINCE","DIECISEIS","DIECISIETE","DIECIOCHO","DIECINUEVE"),
                        ("VEINTE","VEINTI"),("TREINTA","TREINTA Y "),("CUARENTA" , "CUARENTA Y "),
                        ("CINCUENTA" , "CINCUENTA Y "),("SESENTA" , "SESENTA Y "),
                        ("SETENTA" , "SETENTA Y "),("OCHENTA" , "OCHENTA Y "),
                        ("NOVENTA" , "NOVENTA Y ")
                    ]
        lista_unidad = ["",("UN" , "UNO"),"DOS","TRES","CUATRO","CINCO","SEIS","SIETE","OCHO","NUEVE"]
        centena = int (numero / 100)
        decena = int((numero -(centena * 100))/10)
        unidad = int(numero - (centena * 100 + decena * 10))
        #print "centena: ",centena, "decena: ",decena,'unidad: ',unidad
     
        texto_centena = ""
        texto_decena = ""
        texto_unidad = ""
     
        #Validad las centenas
        texto_centena = lista_centana[centena]
        if centena == 1:
            if (decena + unidad)!=0:
                texto_centena = texto_centena[1]
            else :
                texto_centena = texto_centena[0]
     
        #Valida las decenas
        texto_decena = lista_decena[decena]
        if decena == 1 :
             texto_decena = texto_decena[unidad]
        elif decena > 1 :
            if unidad != 0 :
                texto_decena = texto_decena[1]
            else:
                texto_decena = texto_decena[0]
        #Validar las unidades
        #print "texto_unidad: ",texto_unidad
        if decena != 1:
            texto_unidad = lista_unidad[unidad]
            if unidad == 1:
                texto_unidad = texto_unidad[sw]
     
        return "%s %s %s" %(texto_centena,texto_decena,texto_unidad)

    def numero_to_letras(self,numero):
        indicador = [("",""),("MIL","MIL"),("MILLON","MILLONES"),("MIL","MIL"),("BILLON","BILLONES")]
        entero = int(numero)
        decimal = int(round((numero - entero)*100))
        #print 'decimal : ',decimal 
        contador = 0
        numero_letras = ""
        while entero >0:
            a = entero % 1000
            if contador == 0:
                en_letras = self.convierte_cifra(a,1).strip()
            else :
                en_letras = self.convierte_cifra(a,0).strip()
            if a==0:
                numero_letras = en_letras+" "+numero_letras
            elif a==1:
                if contador in (1,3):
                    numero_letras = indicador[contador][0]+" "+numero_letras
                else:
                    numero_letras = en_letras+" "+indicador[contador][0]+" "+numero_letras
            else:
                numero_letras = en_letras+" "+indicador[contador][1]+" "+numero_letras
            numero_letras = numero_letras.strip()
            contador = contador + 1
            entero = int(entero / 1000)
        numero_letras = numero_letras+" con " + str(decimal) +"/100"

        return numero_letras

    def imprimir_contrato(self):
        if not self.contract_type_id.directorio or not self.contract_type_id.directorio_out:
            raise ValidationError("Debe definir las plantillas de documento a usarse para el tipo de contrato")
        clave='contrato_indefinido'
        dct=self.crear_contrato()
        return dct

    def crear_contrato(self,):
        obj_plantilla=self.env['plantillas.dinamicas.informes'].search([('identificador_clave','=','contrato_indefinido')],limit=1)
        if obj_plantilla:
            mesesDic = {
                "1":'Enero',
                "2":'Febrero',
                "3":'Marzo',
                "4":'Abril',
                "5":'Mayo',
                "6":'Junio',
                "7":'Julio',
                "8":'Agosto',
                "9":'Septiembre',
                "10":'Octubre',
                "11":'Noviembre',
                "12":'Diciembre'
            }
            shutil.copy2(self.contract_type_id.directorio,self.contract_type_id.directorio_out)
            campos=obj_plantilla.campos_ids.filtered(lambda l: len(l.child_ids)==0)
            lista_campos=[]
            lista_campos.append({'identificar_docx':'sueldo_letras',
                'valor':self.numero_to_letras(self.wage)})

            for campo in campos:
                dct={}
                resultado=self.mapped(campo.name)
                
                if campo.name!=False:
                    dct={}
                    if len(resultado)>0:
                        if resultado[0]==False:
                            dct['valor']=''
                        else:    
                            dct['valor']=str(resultado[0])
                    else:
                        dct['valor']=''
                dct['identificar_docx']=campo.identificar_docx
                lista_campos.append(dct)
            year = self.date_start.year
            mes = self.date_start.month
            dia = self.date_start.day
            fechacontr = str(dia)+' de '+str(mesesDic[str(mes)])+' del '+str(year)
            dct = {}
            dct['identificar_docx']='txt_actual'
            dct['valor']=fechacontr
            lista_campos.append(dct)
            crear_contrato_doc.crear_contrato_doc(self.contract_type_id.directorio_out,lista_campos)
            with open(self.contract_type_id.directorio_out, "rb") as f:
                data = f.read()
                file=bytes(base64.b64encode(data))
        obj_attch=self.env['ir.attachment'].create({
                                                    'name':'{0}.docx'.format(self.name), 
                                                    'datas':file,
                                                    'type':'binary', 
                                                    'store_fname':'{0}.docx'.format(self.name),
                                                    })

        url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url += "/web/content/%s?download=true" %(obj_attch.id)
        return{
            "type": "ir.actions.act_url",
            "url": url,
            "target": "new",
        }


class hrContractType(models.Model):
    _inherit = 'hr.contract.type'

    directorio = fields.Char(string='Directorio de Plantilla')  
    directorio_out = fields.Char(string='Directorio de Salida de Informe')  