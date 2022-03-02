# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import os
import re
import json
import base64
import logging
import mimetypes
import odoo.tools
import hashlib
from odoo import api, fields, models, tools, SUPERUSER_ID
from datetime import datetime,timedelta,date
import time
from odoo import _
from odoo.exceptions import ValidationError, except_orm
from dateutil.relativedelta import *
from . import informe_excel

import base64
from base64 import urlsafe_b64decode

import shutil



class Nomina_mensual(models.TransientModel):
    _name = "correo.nomina.mensual"

    def _get_available_contracts_domain(self):
        return [('contract_ids.state', 'in', ('open', 'close')), ('company_id', '=', self.env.company.id)]

    def _get_employees(self):
        # YTI check dates too
        return self.env['hr.employee'].search(self._get_available_contracts_domain())

    employee_ids_correo = fields.Many2many('hr.employee', 'payslip_id', 'employee_id', 'Employees',
                                    default=lambda self: self._get_employees(), required=True)

    def send_mail_payrol(self):
        result = self.env['hr.payslip']
        #for l in self.employee_ids_correo:
        #    self.envio_correos_plantilla('correo_nomina_mensual',l.id)
    
    
    def envio_correos_plantilla(self, plantilla,id_envio):

        try:
            ir_model_data = self.env['ir.model.data']
            template_id = ir_model_data.get_object_reference('gzl_reporte', plantilla)[1]
        except ValueError:
            template_id = False
#Si existe capturo el template
        if template_id:
            obj_template=self.env['mail.template'].browse(template_id)

            email_id=obj_template.send_mail(id_envio)  