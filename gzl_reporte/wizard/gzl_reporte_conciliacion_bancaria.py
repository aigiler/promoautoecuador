# -*-  coding: utf-8 -*-
from odoo import api, models,_, fields
from odoo.exceptions import ValidationError, UserError

class bankStatementReport(models.TransientModel):
    _name = 'bank.statement.report'
    _description = _('Report Bank Statement')
    _rec_name = 'journal_id'

    journal_id = fields.Many2one('account.journal', string="Diario", domain="[('type','=','bank')]")
    date = fields.Date(string="Corte")
    saldo_cuenta = fields.Float(string="Saldo Segun Estado de cuenta")
    total_conciliado = fields.Float(string="Total Conciliado")
    total_no_conciliado = fields.Float(string="Total no conciliado")

    diferencia = fields.Float(string="Diferencia")
    subtotal_cheques_no_cobrados = fields.Float(string="Subtotal Cheques")
    subtotal_depositos_no_cobrados = fields.Float(string="Subtotal depositos")
    subtotal_debitos_no_cobrados = fields.Float(string="Subtotal debitos")
    subtotal_creditos_no_cobrados = fields.Float(string="Subtotal creditos")


    subtotal_cheques_no_cobrados_no_cont = fields.Float(string="Subtotal Cheques No Contabilizado")
    subtotal_depositos_no_cobrados_no_cont = fields.Float(string="Subtotal depositos No Contabilizado")
    subtotal_debitos_no_cobrados_no_cont = fields.Float(string="Subtotal debitos No Contabilizado")
    subtotal_creditos_no_cobrados_no_cont = fields.Float(string="Subtotal creditos No Contabilizado")





    def print_report(self):
        self.saldo_cuenta_calculo()


        return self.env.ref('gzl_reporte.bank_statement_report').report_action(self)

    def saldo_cuenta_calculo(self):
        dct=self._get_bank_rec_report_data({'all_entries':False},self.journal_id)
        self.saldo_cuenta=dct['total_already_accounted']

        self.subtotal_depositos_no_cobrados=self.body_report('deposito',True)
        self.subtotal_debitos_no_cobrados=self.body_report('debito',True)
        self.subtotal_cheques_no_cobrados=self.body_report('cheque',True)
        self.subtotal_creditos_no_cobrados=self.body_report('credito',True)

        self.subtotal_cheques_no_cobrados_no_cont = self.body_report('cheque',True,False)
        self.subtotal_depositos_no_cobrados_no_cont = self.body_report('deposito',True,False)
        self.subtotal_debitos_no_cobrados_no_cont = self.body_report('debito',True,False)
        self.subtotal_creditos_no_cobrados_no_cont = self.body_report('credito',True,False)


        self.diferencia= self.saldo_cuenta + self.subtotal_depositos_no_cobrados + self.subtotal_creditos_no_cobrados - self.subtotal_cheques_no_cobrados - self.subtotal_debitos_no_cobrados
    

    def body_report(self, ref=False,valores=False,contabilizado=True):

        if contabilizado:
            state_deposito=state_debito=state_credito='posted'
            state_cheque='registered'
        else:
            state_deposito=state_debito=state_credito='draft'
            state_cheque='draft'


        #Depositos No Incluidos
        if ref=='deposito':

            filtro=[('payment_date','<=',self.date),('invoice_id.type','!=','out_refund'),('payment_type','=','inbound'),('state','=',state_deposito),('check_number','=',False)]

            depositos=self.env['account.payment'].search(filtro)
            if not valores:
                lista_obj=[]
                for deposito in depositos:
                    dct={}
                    dct['numero_documento']=deposito.name or '-'
                    dct['fecha_emision']=deposito.payment_date or '-'
                    dct['referencia']=deposito.communication or '-'
                    dct['empresa']=deposito.partner_id.name 

                    dct['monto']=deposito.amount 

                    obj=self.env['reporte.conciliacion.bancaria.detalle'].create(dct)

                    lista_obj.append(obj)


        #Creditos No Incluidos






        #Creditos No Incluidos
        if ref=='cheque':
            filtro=[]
            if self.journal_id.id:
                filtro=[('journal_id','=',self.journal_id.id),('cheque_date','<=',self.date),('status','=',state_cheque)]
    #######filtro de cheques
            cheques=self.env['account.cheque'].search(filtro)
            
            lista_cheques=[]

            for cheque in cheques:
                dct={}
                dct['numero_cheque']=cheque.cheque_number
                dct['banco']=cheque.journal_id.bank_id.name
                dct['monto']=cheque.amount
                dct['fecha_cheque']=cheque.cheque_date
                dct['empresa']=cheque.payee_user_id.name
                dct['terceros']=cheque.third_party_name

                paymments=self.env['account.payment'].search([('payment_method_id.code','=','check_printing'),('check_number','=',cheque.cheque_number)],limit=1)
                dct['numero_documento_pago']=paymments.name or '-'
                dct['fecha_pago']=paymments.date_to or '-'
                dct['descripcion']=paymments.communication or '-'

                if paymments.id and  paymments.state=='reconciled':
                    dct['conciliado']='Si'
                else:
                    dct['conciliado']='No'

                lista_cheques.append(dct)

            lista_cheques = filter(lambda x: x['conciliado']=='No', lista_cheques)
            lista_obj=[]
            if not valores:

                for cheque in lista_cheques:
                    dct={
                    'numero_documento':cheque['numero_cheque'],
                    'fecha_emision':cheque['fecha_cheque'],
                    'empresa':cheque['empresa'],
                    'referencia':cheque['descripcion'],
                    'monto':cheque['monto'],
                    }
                    obj=self.env['reporte.conciliacion.bancaria.detalle'].create(dct)

                    lista_obj.append(obj)


        #Debitos No Incluidos
        if ref=='debito':

            filtro=[('payment_date','<=',self.date),('payment_type','in',['outbound','transfer']),('state','=',state_deposito),('check_number','=',False)]

            debitos=self.env['account.payment'].search(filtro)
            lista_obj=[]

            if not valores:
                for debito in debitos:
                    dct={}
                    dct['numero_documento']=debito.name or '-'
                    dct['fecha_emision']=debito.payment_date or '-'
                    dct['referencia']=debito.communication or '-'
                    dct['empresa']=debito.partner_id.name 

                    dct['monto']=debito.amount 

                    obj=self.env['reporte.conciliacion.bancaria.detalle'].create(dct)

                    lista_obj.append(obj)




        #Debitos No Incluidos
        if ref=='credito':

            filtro=[('payment_date','<=',self.date),('invoice_id.type','=','out_refund'),('payment_type','in',['inbound']),('state','=',state_credito),('check_number','=',False)]

            creditos=self.env['account.payment'].search(filtro)
            lista_obj=[]
            if not valores:     
                for credito in creditos:
                    dct={}
                    dct['numero_documento']=credito.name or '-'
                    dct['fecha_emision']=credito.payment_date or '-'
                    dct['referencia']=credito.communication or '-'
                    dct['empresa']=credito.partner_id.name 

                    dct['monto']=credito.amount 

                    obj=self.env['reporte.conciliacion.bancaria.detalle'].create(dct)

                    lista_obj.append(obj)


        if valores:
            if ref=='deposito':
                return float(sum(depositos.mapped('amount')))
            if ref=='debito':
                return float(sum(debitos.mapped('amount')))
            if ref=='cheque':
                return float(sum(map(lambda x: x['monto'],lista_cheques)))
            if ref=='credito':
                return float(sum(creditos.mapped('amount')))
        else:
            return lista_obj



    @api.model
    def _get_bank_rec_report_data(self, options, journal):
        # General data + setup
        rslt = {}

        accounts = journal.default_debit_account_id + journal.default_credit_account_id
        company = journal.company_id
        amount_field = 'balance' if (not journal.currency_id or journal.currency_id == journal.company_id.currency_id) else 'amount_currency'
        states = ['posted']
        states += options.get('all_entries') and ['draft'] or []

        # Get total already accounted.
        self._cr.execute('''
            SELECT SUM(aml.''' + amount_field + ''')
            FROM account_move_line aml
            LEFT JOIN account_move am ON aml.move_id = am.id
            WHERE aml.date <= %s AND aml.company_id = %s AND aml.account_id IN %s
            AND am.state in %s
        ''', [self.env.context['date'], journal.company_id.id, tuple(accounts.ids), tuple(states)])
        rslt['total_already_accounted'] = self._cr.fetchone()[0] or 0.0

        # Payments not reconciled with a bank statement line
        self._cr.execute('''
            SELECT
                aml.id,
                aml.name,
                aml.ref,
                aml.date,
                aml.''' + amount_field + '''                    AS balance
            FROM account_move_line aml
            LEFT JOIN res_company company                       ON company.id = aml.company_id
            LEFT JOIN account_account account                   ON account.id = aml.account_id
            LEFT JOIN account_account_type account_type         ON account_type.id = account.user_type_id
            LEFT JOIN account_bank_statement_line st_line       ON st_line.id = aml.statement_line_id
            LEFT JOIN account_payment payment                   ON payment.id = aml.payment_id
            LEFT JOIN account_journal journal                   ON journal.id = aml.journal_id
            LEFT JOIN account_move move                         ON move.id = aml.move_id
            WHERE aml.date <= %s
            AND aml.company_id = %s
            AND CASE WHEN journal.type NOT IN ('cash', 'bank')
                     THEN payment.journal_id
                     ELSE aml.journal_id
                 END = %s
            AND account_type.type = 'liquidity'
            AND full_reconcile_id IS NULL
            AND (aml.statement_line_id IS NULL OR st_line.date > %s)
            AND (company.account_bank_reconciliation_start IS NULL OR aml.date >= company.account_bank_reconciliation_start)
            AND move.state in %s
            ORDER BY aml.date DESC, aml.id DESC
        ''', [self._context['date'], journal.company_id.id, journal.id, self._context['date'], tuple(states)])
        rslt['not_reconciled_payments'] = self._cr.dictfetchall()

        # Bank statement lines not reconciled with a payment
        rslt['not_reconciled_st_positive'] = self.env['account.bank.statement.line'].search([
            ('statement_id.journal_id', '=', journal.id),
            ('date', '<=', self._context['date']),
            ('journal_entry_ids', '=', False),
            ('amount', '>', 0),
            ('company_id', '=', company.id)
        ])

        rslt['not_reconciled_st_negative'] = self.env['account.bank.statement.line'].search([
            ('statement_id.journal_id', '=', journal.id),
            ('date', '<=', self._context['date']),
            ('journal_entry_ids', '=', False),
            ('amount', '<', 0),
            ('company_id', '=', company.id)
        ])

        # Final
        last_statement = self.env['account.bank.statement'].search([
            ('journal_id', '=', journal.id),
            ('date', '<=', self._context['date']),
            ('company_id', '=', company.id)
        ], order="date desc, id desc", limit=1)
        rslt['last_st_balance'] = last_statement.balance_end
        rslt['last_st_end_date'] = last_statement.date

        return rslt









    def print_report_xls(self):
        file_data = BytesIO()
        workbook = xlsxwriter.Workbook(file_data)
        name = 'Reporte de Conciliacion Bancaria {0}'.format(self.journal_id.name)
        self.xslx_body(workbook, name)
        

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






        
    def xslx_body(self, workbook, name):
        bold = workbook.add_format({'bold':True,'border':1})
        bold_no_border = workbook.add_format({'bold':True})
        bold.set_center_across()
        format_title = workbook.add_format({'bold':True,'border':1})
        format_title_left = workbook.add_format({'bold':True,'border':1,'align': 'left'})
        format_title_left_14 = workbook.add_format({'bold':True,'border':1,'align': 'left','size': 14})
        format_title_center_14 = workbook.add_format({'bold':True,'border':1,'align': 'center','size': 14})


        format_title.set_center_across()
        currency_format = workbook.add_format({'num_format': '[$$-409]#,##0.00','border':1,'text_wrap': True })
        currency_format.set_align('vcenter')

        
        date_format = workbook.add_format({'num_format': 'dd/mm/yy', 'align': 'right','border':1,'text_wrap': True })
        date_format.set_align('vcenter')
        date_format_day = workbook.add_format({'align': 'right','border':1,'text_wrap': True })
        date_format_day.set_align('vcenter')
        date_format_title = workbook.add_format({'num_format': 'dd/mm/yy', 'align': 'left','text_wrap': True})
        date_format_title.set_align('vcenter')

        body = workbook.add_format({'align': 'center' , 'border':1,'text_wrap': True})
        body.set_align('vcenter')
        body_right = workbook.add_format({'align': 'right', 'border':1 })
        body_left = workbook.add_format({'align': 'left','bold':True})
        format_title2 = workbook.add_format({'align': 'center', 'bold':True,'border':1 })
        sheet = workbook.add_worksheet(name)

        sheet.set_portrait()
        sheet.set_paper(9)  # A4

        sheet.set_margins(left=0.4, right=0.4, top=0.4, bottom=0.2)
        sheet.set_print_scale(100)
        sheet.fit_to_pages(1,2)



        
        sheet.merge_range('A1:G1', self.env.company.name.upper(), workbook.add_format({'bold':True,'border':0,'align': 'left','size': 14}))
        sheet.merge_range('A2:G2', 'RUC: '+self.env.company.vat, workbook.add_format({'bold':True,'border':0,'align': 'left'}))
        sheet.merge_range('A3:G3', 'Dirección: '+self.env.company.street, workbook.add_format({'bold':True,'border':0,'align': 'left'}))
        sheet.merge_range('A4:G4', 'Teléfono: '+self.env.company.phone, workbook.add_format({'bold':True,'border':0,'align': 'left'}))

        sheet.merge_range('A5:G5', 'CONCILIACIÓN BANCARIA', workbook.add_format({'bold':True,'border':0,'align': 'center','size': 14}))
        bold.set_bg_color('b8cce4')
        
        
        date_format_title_no_border=workbook.add_format({'align': 'center' ,'bold':True, 'border':0,'text_wrap': True})
        date_format_title_no_border.set_bg_color('b8cce4')
        sheet.write(5,1, 'Fecha Corte:', date_format_title_no_border)
        sheet.write(5,2,self.date, workbook.add_format({'num_format': 'dd/mm/yy', 'align': 'right','border':0,'text_wrap': True }))
        date_format_title_no_border.set_bg_color('b8cce4')


        sheet.merge_range('A1:G1', self.env.company.name.upper(), workbook.add_format({'bold':True,'border':0,'align': 'left','size': 14}))
        sheet.merge_range('A2:G2', 'RUC: '+self.env.company.vat, workbook.add_format({'bold':True,'border':0,'align': 'left'}))
        sheet.merge_range('A3:G3', 'Dirección: '+self.env.company.street, workbook.add_format({'bold':True,'border':0,'align': 'left'}))
        sheet.merge_range('A4:G4', 'Teléfono: '+self.env.company.phone, workbook.add_format({'bold':True,'border':0,'align': 'left'}))

        sheet.merge_range('A5:G5', 'CONCILIACIÓN BANCARIA', workbook.add_format({'bold':True,'border':0,'align': 'center','size': 14}))
        bold.set_bg_color('b8cce4')




        title_main=['Documento','Fc. Emisión', 'Fc.Vencimiento', 'Anticipo','Aplicación', 'Saldo', 'Observaciones']
        bold.set_bg_color('b8cce4')

        ##Titulos
        colspan=4
        for col, head in enumerate(title_main):
            sheet.set_column('{0}:{0}'.format(chr(col + ord('A'))), len(head) + 7)
            sheet.write(7, col, head, bold)

            
        sheet.set_column('A:A', 23)
        sheet.set_column('B:B', 23)
        sheet.set_column('H:H', 60)

        filtro=[('payment_date','>=',self.date_from),
            ('payment_date','<=',self.date_to),('tipo_transaccion','=','Anticipo')]

        lista_partner=self.obtener_listado_partner_payment(filtro)
        fila=8
        filas_total_partner=[]
        for partner in lista_partner:
            filtro=[('payment_date','>=',self.date_from),
                ('payment_date','<=',self.date_to),('tipo_transaccion','=','Anticipo')]
            lista_anticipos=self.obtener_listado_payment_por_empresa(partner['id'],filtro)

            if len(lista_anticipos)>0:
                sheet.write(fila, 0, partner['nombre'], workbook.add_format({'bold':True,'border':0}))
                fila+=1
                line = itertools.count(start=fila)
                fila_current=0
                for anticipo in lista_anticipos:
                    current_line = next(line)

                    sheet.write(current_line, 0, anticipo['numero_documento'] or "", body)
                    sheet.write(current_line, 1, anticipo['fecha_emision'] or "", date_format)
                    sheet.write(current_line, 2, anticipo['fecha_vencimiento'] or "", date_format)
                    sheet.write(current_line, 3, anticipo['monto_anticipo'] ,currency_format)
                    sheet.write(current_line, 4, anticipo['monto_aplicado'] ,currency_format)
                    sheet.write(current_line, 5, anticipo['monto_adeudado']  ,currency_format)
                    sheet.write(current_line, 6,  anticipo['observaciones'] or "" ,body)
                    fila_current=current_line

                bold_right=workbook.add_format({'bold':True,'border':1,'align':'right'})
                bold_right.set_bg_color('d9d9d9')

                sheet.merge_range('A{0}:C{0}'.format(fila_current+2), 'Total '+ partner['nombre'], bold_right)

                lista_col_formulas=[3,4,5]
                for col in lista_col_formulas:
                    col_formula = {
                            'from_col': chr(65 +col),
                            'to_col': chr(65 +col),
                            'from_row': fila+1,
                            'to_row': fila_current+1,                

                        }
                    currency_bold=workbook.add_format({'num_format': '[$$-409]#,##0.00','border':1,'text_wrap': True ,'bold':True})
                    currency_bold.set_bg_color('d9d9d9')

                    sheet.write_formula(
                                fila_current+1 ,col ,
                                '=SUM({from_col}{from_row}:{to_col}{to_row})'.format(
                                    **col_formula
                                ), currency_bold)
                filas_total_partner.append(fila_current+2)

                fila=fila_current+3

                
                
                
                
                
                
                
                
  
        lista_col_formulas=[3,4,5]
        
        if len(lista_partner)>0:

            bold_right=workbook.add_format({'bold':True,'border':1,'align':'right'})
            bold_right.set_bg_color('d9d9d9')

            sheet.merge_range('A{0}:C{0}'.format(fila_current+3), 'Total General', bold_right)

              

            
            for columna in lista_col_formulas:

                currency_bold=workbook.add_format({'num_format': '[$$-409]#,##0.00','border':1,'text_wrap': True ,'bold':True})
                currency_bold.set_bg_color('d9d9d9')


                formula='='
                for fila_total in filas_total_partner:
                    formula=formula+'{0}{1}'.format(chr(65 +columna),fila_total)+'+'
                formula=formula.rstrip('+')
                sheet.write(
                            fila_current+2 ,columna ,
                            formula, currency_bold)





























class ReporteAnticipoDetalle(models.TransientModel):
    _name = "reporte.conciliacion.bancaria.detalle"

    numero_documento = fields.Char('Nro. Documento')
    fecha_emision = fields.Date('Fc. Emision')
    empresa = fields.Char('Empresa')
    referencia = fields.Char('Referencia')
    monto = fields.Float('Monto ')
    observaciones = fields.Char('Observaciones')
    reglon = fields.Char('Reglon')

