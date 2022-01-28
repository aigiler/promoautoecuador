# -*- coding: utf-8 -*-

import re
from docx import Document







def crear_documento_reserva(ruta,detalle,lista_estado_cuenta ):
    #Se abre el documento en la ruta
    doc = Document(ruta)

    # #Tabla de Alarmas Rojas
    tabla=doc.tables[1]



    contador=1
    for estado_cuenta in lista_estado_cuenta:
        if estado_cuenta['numero_cuota']!=False:
            tabla.cell(contador, 0).text = str(estado_cuenta.numero_cuota)
        if estado_cuenta['fecha']!=False:
            tabla.cell(contador, 1).text = str(estado_cuenta.fecha)
        if estado_cuenta['cuota_capital']!=False:
            tabla.cell(contador, 2).text = str(estado_cuenta.cuota_capital)
        if estado_cuenta['cuota_adm']!=False:
            tabla.cell(contador, 3).text = str(estado_cuenta.cuota_adm)
        if estado_cuenta['iva_adm']!=False:
            tabla.cell(contador, 4).text = str(estado_cuenta.iva_adm)
        if estado_cuenta['saldo']!=False:
            tabla.cell(contador, 5).text = str(estado_cuenta.saldo)
        contador+=1
        if contador!=len(dct_final['estado_cuenta'])+1:
            tabla.add_row() 

    for campo in detalle:
        #Redenriza
        regex1 = re.compile(campo['identificar_docx'])

      #  Reemplaza los valores de identificadores de la plantilla con los del json
        docx_replace_regex_ram(doc,regex1,campo['valor'])
        docx_replace_regex_header_ram(doc.sections[0].header,regex1,campo['valor'])

 


    


    doc.save(ruta)


def identificar_parrafo(doc_obj, regex):

    for p in doc_obj.paragraphs:
        if regex.search(p.text):
            return p






def docx_replace_regex_header_ram(doc_obj, regex , replace):

    for p in doc_obj.paragraphs:
        if regex.search(p.text):

            inline = p.runs


            # Loop added to work with runs (strings with same style)
            for i in range(len(inline)):

                if regex.search(inline[i].text):
                    text = regex.sub(replace, inline[i].text)
                    inline[i].text = text

    for table in doc_obj.tables:
        for row in table.rows:
            for cell in row.cells:
                docx_replace_regex_ram(cell, regex , replace)









def docx_replace_regex_ram(doc_obj, regex , replace):

    for p in doc_obj.paragraphs:
        if regex.search(p.text):
            inline = p.runs

            # Loop added to work with runs (strings with same style)
            for i in range(len(inline)):
                if regex.search(inline[i].text):
                    text = regex.sub(replace, inline[i].text)
                    inline[i].text = text

    for table in doc_obj.tables:
        for row in table.rows:
            for cell in row.cells:
                docx_replace_regex_ram(cell, regex , replace)

