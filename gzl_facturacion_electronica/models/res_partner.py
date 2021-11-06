# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    ats_regimen_fiscal = fields.Many2one('ats.regimen.fiscal', string="Regimen Fiscal")
    ats_regimen_fiscal_code = fields.Char(related='ats_regimen_fiscal.code') 
    ats_residente = fields.Many2one('ats.pago.residente' ,string="Tipo de pago")
    ats_residente_code = fields.Char(related='ats_residente.code') 
    is_aduana = fields.Boolean('Es Aduanas', default=False)
    is_transporter = fields.Boolean('Transportista', default=False)
    license_number = fields.Char(string='Número de Licencia')
    is_cont_especial = fields.Boolean('Codigo Contribuyente Especial')
    is_rise = fields.Boolean('RISE')


    ats_country = fields.Many2one('ats.country', string='Pais')
    ats_country_efec_gen = fields.Many2one('ats.country', string='Pais Efec')
    ats_country_efec_parfic = fields.Many2one('ats.country', string='Pais Efec ParFis')
    ats_doble_trib = fields.Boolean('Aplica doble tributacion', default=False)
    denopago = fields.Char('Denominacion', help='Denominación del régimen fiscal preferente o jurisdicción de menor imposición.')
    pag_ext_suj_ret_nor_leg = fields.Boolean('Sujeto a retencion', help='Pago al exterior sujeto a retención en aplicación a la norma legal', default=False)
    pago_reg_fis = fields.Boolean('Regimen Fiscal Preferente', help='El pago es a un régimen fiscal preferente o de menor imposición?', default=False)
    method_payment = fields.Many2one('account.epayment', string="Forma de Pago")
    