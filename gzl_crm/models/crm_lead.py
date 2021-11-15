# -*- coding: utf-8 -*-

from odoo import api, fields, models
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError

import numpy_financial as npf


class CrmLead(models.Model):
    
    _inherit = 'crm.lead'

    is_won = fields.Boolean(related='stage_id.is_won')
    contacto_name = fields.Char(string='Nombre Completo')
    contacto_cedula = fields.Char(string='Cédula')
    contacto_correo = fields.Char(string='Correo Electrónico')
    contacto_telefono = fields.Char(string='Teléfono')
    contacto_domicilio = fields.Char(string='Domicilio')
    tasa_interes = fields.Integer(string='Tasa de Inter+és')
    numero_cuotas = fields.Integer(string='Número de Cuotas')
    dia_pago = fields.Integer(string='Día de Pagos')
    tipo_contrato = fields.Many2one('tipo.contrato.adjudicado', string='Tipo de Contrato')
    tabla_amortizacion = fields.One2many('tabla.amortizacion', 'oportunidad_id' )
    cotizaciones_ids = fields.One2many('sale.order', 'oportunidad_id')

    def detalle_tabla_amortizacion(self):
        self._cr.execute(""" delete from tabla_amortizacion where oportunidad_id={0}""".format(self.id))
        capital = self.planned_revenue
        tasa = self.tasa_interes/100
        plazo = self.numero_cuotas
        cuota = round(npf.pmt(tasa, plazo, -capital, 0), 0)
        saldo = capital
        ahora = datetime.now()
        try:
            ahora = ahora.replace(day = self.dia_pago)
        except:
            raise ValidationError('La fecha no existe, por favor ingrese otro día de pago.')
        for i in range(1, plazo+1):
            pago_capital = npf.ppmt(tasa, i, plazo, -capital, 0)
            pago_int = cuota - pago_capital
            saldo -= pago_capital  
            self.env['tabla.amortizacion'].create({'oportunidad_id':self.id,
                                                   'numero_cuota':i,
                                                   'fecha':ahora + relativedelta(months=i),
                                                   'cuota':cuota,
                                                   'capital':pago_capital,
                                                   'interes':pago_int,
                                                   'saldo':saldo
                                                    })
                                            
                                               
    def crear_adjudicado(self):
        if self.stage_id.is_won:
            self.env['res.partner'].create({
                                        'name':self.partner_id.name,
                                        'type':'contact',
                                        'tipo':'adjudicado',
                                        'monto':self.planned_revenue or 0,
                                        'function':self.partner_id.function or None,
                                        'email':self.partner_id.email or None,
                                        'phone':self.partner_id.phone or None,
                                        'mobile':self.partner_id.mobile or None,
                                        })

    
    def crear_contrato(self):
        plantillas = self.env['sign.template'].search([('attachment_id.tipo_plantilla','=','adjudicacion')])
        for l in plantillas:
            def create_request(self, send=True, without_mail=False):
                template_id = l.id
                signers = [{'partner_id': self.partner_id.id, 'role': False}]
                followers = []
                reference = l.attachment_id.name
                subject = 'Contrato'
                message = 'Contrato'
                return self.env['sign.request'].initialize_new(l.id, signers, followers, reference, subject, message, send, without_mail)
            a=create_request(self)
            sign_request=self.env['sign.request'].search([('id','=',a['id'])])
            def sign_directly_without_mail(self):
                #res = create_request(False, True)
                request = self.env['sign.request'].browse(sign_request.id)
                user_item = request.request_item_ids[0]
                return {
                    'type': 'ir.actions.client',
                    'tag': 'sign.SignableDocument',
                    'name': _('Sign'),
                    'context': {
                        'id': request.id,
                        'token': user_item.access_token,
                        'sign_token': user_item.access_token,
                        'create_uid': request.create_uid.id,
                        'state': request.state,
                        # Don't use mapped to avoid ignoring duplicated signatories
                        'token_list': [item.access_token for item in request.request_item_ids[1:]],
                        'current_signor_name': user_item.partner_id.name,
                        'name_list': [item.partner_id.name for item in request.request_item_ids[1:]],
                    },
                }
            
            def send_completed_document(self):
                self.ensure_one()
                self.contacto_cedula = "entra a send_completed_document"
                if len(sign_request.request_item_ids) <= 0 or self.state != 'signed':
                    self.contacto_correo = 'linea 107'
                    return False
                    

                if not sign_request.completed_document:
                    sign_request.generate_completed_document()

                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                attachment = self.env['ir.attachment'].create({
                    'name': "%s.pdf" % sign_request.reference if sign_request.reference.split('.')[-1] != 'pdf' else sign_request.reference,
                    'datas': sign_request.completed_document,
                    'type': 'binary',
                    'res_model': sign_request._name,
                    'res_id': sign_request.id,
                })
                self.contacto_name= attachment
                report_action = self.env.ref('sign.action_sign_request_print_logs')
                # print the report with the public user in a sudoed env
                # public user because we don't want groups to pollute the result
                # (e.g. if the current user has the group Sign Manager,
                # some private information will be sent to *all* signers)
                # sudoed env because we have checked access higher up the stack
                public_user = self.env.ref('base.public_user', raise_if_not_found=False)
                if not public_user:
                    # public user was deleted, fallback to avoid crash (info may leak)
                    public_user = self.env.user
                pdf_content, __ = report_action.with_user(public_user).sudo().render_qweb_pdf(self.id)
                attachment_log = self.env['ir.attachment'].create({
                    'name': "Activity Logs - %s.pdf" % time.strftime('%Y-%m-%d - %H:%M:%S'),
                    'datas': base64.b64encode(pdf_content),
                    'type': 'binary',
                    'res_model': sign_request._name,
                    'res_id': sign_request.id,
                })
                tpl = self.env.ref('sign.sign_template_mail_completed')
                for signer in sign_request.request_item_ids:
                    if not signer.signer_email:
                        continue
                    signer_lang = get_lang(self.env, lang_code=signer.partner_id.lang).code
                    tpl = tpl.with_context(lang=signer_lang)
                    body = tpl.render({
                        'record': self,
                        'link': url_join(base_url, 'sign/document/%s/%s' % (sign_request.id, signer.access_token)),
                        'subject': '%s signed' % self.reference,
                        'body': False,
                    }, engine='ir.qweb', minimal_qcontext=True)

                    
                return True
    

    
    @api.onchange('stage_id.is_won')
    def crear_factura_automatica(self):
        if self.stage_id.is_won:
            view_id = self.env.ref('gzl_crm.wizard_cotizaciones_crm').id
            return {'type': 'ir.actions.act_window',
                    'name': _('Cotizaciones'),
                    'res_model': 'sale.order',
                    'target': 'new',
                    'view_mode': 'form',
                    'views': [[view_id, 'form']],
                    'domain': [('oportunidad_id', '=', self.id)],
                    'context': {'oportunidad_id': self.id}
            }

    


class TablaAmortizacion(models.Model):
    _name = 'tabla.amortizacion'
    _description = 'Tabla de Amortización'

    oportunidad_id = fields.Many2one('crm.lead')
    numero_cuota = fields.Char(String='Número de Cuota')
    fecha = fields.Date(String='Fecha')
    currency_id = fields.Many2one('res.currency', readonly=True, default=lambda self: self.env.company.currency_id)
    cuota = fields.Monetary(string='Cuota', currency_field='currency_id')
    capital = fields.Monetary(string='Capital', currency_field='currency_id')
    interes = fields.Monetary(string='Interes', currency_field='currency_id')
    saldo = fields.Monetary(string='Saldo', currency_field='currency_id')
    estado_pago = fields.Selection([('pendiente', 'Pendiente'), 
                                      ('pagado', 'Pagado')
                                    ],string='Estado de Pago', default='pendiente') 
    factura_id = fields.Many2one('account.move')
    pago_id = fields.Many2one('account.payment')
    
    def pagar_cuota(self):
        print("---")
        
    def accion_planificada_crear_factura_borrador(self):
        fecha_borrador= datetime.today() + timedelta(days=-5)
        pagos_pendientes = self.env['tabla.amortizacion'].search([
                                                                ('estado_pago','=','pendiente'),
                                                                #('fecha','>=',fecha_borrador),
                                                                #('factura_id','!=', 0)
                                                                ])
        if pagos_pendientes:
            for l in pagos_pendientes:
                l.oportunidad_id.contacto_name=fecha_borrador
                factura = self.env['account.move'].create({
                            'type': 'out_invoice',
                            'partner_id': l.oportunidad_id.partner_id.id,
                            'invoice_line_ids': [(0, 0, {
                                'quantity': 1,
                                'price_unit': l.cuota,
                                'name': l.oportunidad_id.name+' - Cuota '+l.numero_cuota,
                            })],
                        })
                l.factura_id=factura
                
                pago = self.env['account.payment'].create({
                        'payment_date': l.fecha,
                        'communication': l.oportunidad_id.name+' - Cuota '+l.numero_cuota,
                        'invoice_ids': [(6, 0, [factura.id])],
                        'payment_type': 'inbound',
                        'amount': l.cuota,
                        'partner_id': l.oportunidad_id.partner_id.id,
                        })
                l.pago_id = pago
    
    
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    oportunidad_id = fields.Many2one('crm.lead')