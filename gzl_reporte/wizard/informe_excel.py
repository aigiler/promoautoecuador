# -*- coding: utf-8 -*-
import openpyxl
from openpyxl import Workbook
import openpyxl.worksheet
import unicodedata
from string import ascii_letters
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Border, Side, Alignment, Protection, Font
from openpyxl.styles.borders import Border, Side
from openpyxl.drawing.image import Image
import time
from datetime import datetime,timedelta,date
import calendar
import locale


global root


def crear_wb():
    wb = Workbook(write_only=False, iso_dates=False)
    return wb


def unicodeText(text):
    try:
        text = unicodedata.unicode(text, 'utf-8')
    except TypeError:
        return text

def crea_hoja(wb, title, flag):
    if(flag == 0):
        sheet = wb.active
        sheet.sheet_properties.pageSetUpPr.fitToPage = True

        sheet.page_setup.fitToWidht = False
    if(flag == 1):
        sheet = wb.create_sheet()
        sheet.sheet_properties.pageSetUpPr.fitToPage = True

        sheet.page_setup.fitToWidht = False
    sheet.title = title
    return sheet

# Ajustar tamanios de celdas
def ajustar_hoja(sheet, flag, celda, value):
    if (flag == 0):
        sheet.column_dimensions[celda].width = value
    if (flag == 1):
        sheet.row_dimensions[int(celda)].height = value




def informe_credito_cobranza(ruta,lista):

    workbook = openpyxl.load_workbook(ruta)

    sheet = workbook.active

    listaSheet1 = list(filter(lambda x: (x['hoja']==1), lista)) 



    for campo in listaSheet1:

       # fila=capturar_fila_de_valor_a_buscar_en_hoja_calculo(sheet,5,8,3,campo['valor'])


        cell = sheet.cell(row=campo['fila'], column=campo['columna'])
        cell.value = campo['valor']


    sheet = workbook['Aprobacion']
    sheet = workbook['Liquidacion']
    sheet = workbook['Orden Compra']
    listaSheet2 = list(filter(lambda x: (x['hoja']==2), lista)) 
    listaSheet3 = list(filter(lambda x: (x['hoja']==3), lista)) 
    listaSheet4 = list(filter(lambda x: (x['hoja']==4), lista)) 

###########Llenar segundo sheet
    for campos in listaSheet2:
        cell = sheet.cell(row=campos['fila'], column=campos['columna'])
        cell.value = campos['valor']

    for camposLiq in listaSheet3:
        cell = sheet.cell(row=camposLiq['fila'], column=camposLiq['columna'])
        cell.value = camposLiq['valor']


    for camposOrden in listaSheet4:
        cell = sheet.cell(row=camposOrden['fila'], column=camposOrden['columna'])
        cell.value = camposOrden['valor']

    workbook.save(ruta)





















def informe_formato_alarmas(ruta,lista,detalle):

    workbook = openpyxl.load_workbook('/mnt/extra-addons/muk_dms/static/src/php/Gestor_Informes'+ruta)

    sheet = workbook.active

    for campo in lista:
        cell = sheet.cell(row=campo['fila'], column=campo['columna'])
        cell.value = campo['valor']

    for linea in detalle:
        print("---------------------------------Ingresa")
        nombre_zona=linea['nombre']


        fila=capturar_fila_de_valor_a_buscar_en_hoja_calculo(sheet,8,23,1,nombre_zona)
        print(fila)
        if fila:
            for campo in linea['campos']:
                print(campo['columna'])
                if campo['columna']==6:
                    cell = sheet.cell(row=8, column=campo['columna'])
                else:
                    cell = sheet.cell(row=fila, column=campo['columna'])

                cell.value = campo['valor']
            continue



        fila=capturar_fila_de_valor_a_buscar_en_hoja_calculo(sheet,26,41,1,nombre_zona)
        print(fila)
        if fila:
            for campo in linea['campos']:
                if campo['columna']==6:
                    cell = sheet.cell(row=26, column=campo['columna'])
                else:
                    cell = sheet.cell(row=fila, column=campo['columna'])


                cell.value = campo['valor']
            continue



        fila=capturar_fila_de_valor_a_buscar_en_hoja_calculo(sheet,8,23,9,nombre_zona)
        print(fila)


        if fila:
            for campo in linea['campos']:

                if (campo['columna']+8)==14:
                    cell = sheet.cell(row=8, column=campo['columna']+8)
                else:
                    cell = sheet.cell(row=fila, column=campo['columna']+8)

                cell.value = campo['valor']
            continue




        fila=capturar_fila_de_valor_a_buscar_en_hoja_calculo(sheet,26,41,9,nombre_zona)
        print(fila)
        if fila:
            for campo in linea['campos']:

                if (campo['columna']+8)==14:
                    cell = sheet.cell(row=26, column=campo['columna']+8)
                else:
                    cell = sheet.cell(row=fila, column=campo['columna']+8)



                cell = sheet.cell(row=fila, column=campo['columna']+8)
                cell.value = campo['valor']
            continue

    workbook.save('/mnt/extra-addons/muk_dms/static/src/php/Gestor_Informes'+ruta)




def informe_formato_cctv(ruta,lista,detalle_dvr,detalle_puertas_acceso,detalle_sargent,detalle_cyber,detalle_cerradura):

    workbook = openpyxl.load_workbook('/mnt/extra-addons/muk_dms/static/src/php/Gestor_Informes'+ruta)

    sheet = workbook.active

    for campo in lista:
        cell = sheet.cell(row=campo['fila'], column=campo['columna'])
        cell.value = campo['valor']

        contador=0
        i=0
        j=0
        l=0
        for linea in detalle_dvr:
            if i==0 or i==1:

                for campo in linea['campos']:
                    cell = sheet.cell(row=campo['fila']+(i*10), column=campo['columna'])
                    cell.value = campo['valor']


                for canal in linea['canales']:
                    nombre_canal=canal['nombre']


                    fila=capturar_fila_de_valor_a_buscar_en_hoja_calculo(sheet,4+(i*10),11+(i*10),4,nombre_canal)
                    if fila:
                        for campo in canal['campos']:
                            cell = sheet.cell(row=fila, column=campo['columna'])
                            cell.value = campo['valor']
                    fila=capturar_fila_de_valor_a_buscar_en_hoja_calculo(sheet,4+(i*10),11+(i*10),8,nombre_canal)
                    if fila:
                        for campo in canal['campos']:

                            cell = sheet.cell(row=fila, column=campo['columna'])
                            cell.value = campo['valor']
                i+=1

            if j==1:
                for campo in linea['campos']:
                    cell = sheet.cell(row=campo['fila']+(l*10), column=campo['columna']+(j*11))
                    cell.value = campo['valor']


                for canal in linea['canales']:
                    nombre_canal=canal['nombre']


                    fila=capturar_fila_de_valor_a_buscar_en_hoja_calculo(sheet,4+(l*10),11+(l*10),4+(j*11),nombre_canal)
                    if fila:
                        for campo in canal['campos']:
                            cell = sheet.cell(row=fila, column=campo['columna']+(j*11))
                            cell.value = campo['valor']
                    fila=capturar_fila_de_valor_a_buscar_en_hoja_calculo(sheet,4+(l*10),11+(l*10),8+(j*11),nombre_canal)
                    if fila:
                        for campo in canal['campos']:
                            cell = sheet.cell(row=fila, column=campo['columna']+(j*11))
                            cell.value = campo['valor']
                l+=1

            if i==2:
                j=1

            contador+=1
            if contador==4:
                break

        contador=0
        j=0
        for linea in detalle_puertas_acceso:

            for campo in linea['campos']:
                cell = sheet.cell(row=campo['fila'], column=campo['columna']+(j*5))
                cell.value = campo['valor']


            for canal in linea['puertas']:
                nombre_canal=canal['nombre']


                fila=capturar_fila_de_valor_a_buscar_en_hoja_calculo(sheet,23,26,4+(j*5),nombre_canal)
                print(fila)
                if fila:
                    for campo in canal['campos']:
                        cell = sheet.cell(row=fila, column=campo['columna']+(j*5))
                        cell.value = campo['valor']
            j+=1

            contador+=1
            if contador==2:
                break


        contador=0

        for linea in detalle_sargent:

            for campo in linea['campos']:
                cell = sheet.cell(row=campo['fila'], column=campo['columna'])
                cell.value = campo['valor']
            contador+=1
            if contador==1:
                break




        contador=0

        for linea in detalle_cyber:

            for campo in linea['campos']:
                cell = sheet.cell(row=campo['fila'], column=campo['columna'])
                cell.value = campo['valor']
            contador+=1
            if contador==1:
                break



        j=0

        for linea in detalle_cerradura:

            for campo in linea['campos']:
                cell = sheet.cell(row=campo['fila'], column=campo['columna']+(j*3))
                cell.value = campo['valor']
            j+=1
            if j==2:
                break














    workbook.save('/mnt/extra-addons/muk_dms/static/src/php/Gestor_Informes'+ruta)












def capturar_fila_de_valor_a_buscar_en_hoja_calculo(sheet,fila_ini,fila_fin,columna_eje,nombre_buscar):


    for fila in range(fila_ini,fila_fin+1):
        valor = sheet.cell(row=fila, column=columna_eje)

        print(valor,nombre_buscar)
        if valor.value==nombre_buscar:
            return fila
    return False



def Todalatabla(sheet, col, colfin, fil, filfin, styleleft, styletop, styleright, stylebottom):

    colfin=colfin+1
    filfin=filfin+2

    border_cell = Border(left=Side(style=styleleft), top=Side(style=styletop), right=Side(style=styleright), bottom=Side(style=stylebottom))
    for i in range(fil, filfin-1):
        for j in range(col, colfin):
            sheet.cell(row=i, column=j).border = border_cell




def border_cell(sheet, fil, col, styleleft, styletop, styleright, stylebottom):
    border_cell = Border(left=Side(style=styleleft), top=Side(style=styletop), right=Side(style=styleright), bottom=Side(style=stylebottom))
    sheet.cell(row=fil, column=col).border = border_cell
