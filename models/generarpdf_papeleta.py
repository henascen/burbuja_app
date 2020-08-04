#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 14:18:51 2020

@author: henry
"""
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF
import os
 
def generar_pdf(inicio, final, inombre, ifecha, imateria, icarnet, formato_path, fuente_titulo, fuente_numero, salida):
    #Importar la imagen del formato para la papeleta
    formato = Image.open(formato_path)
    #Redimensionar la imagen para trabajar más eficientemente
    maxsize = (600, 464)
    formato.thumbnail(maxsize, Image.ANTIALIAS)
    #Crear un elemento tipo Draw para modificar el formato existente
    dibujoFormato = ImageDraw.Draw(formato)
    #Crear el documento PDF
    pdf = FPDF(orientation='P', unit='mm', format='letter')
    #Crear las fuentes para el texto a incluir
    tituloFont = ImageFont.truetype(fuente_titulo, 18)
    numeroFont = ImageFont.truetype(fuente_numero, 18)
    
    if(inombre == True):
        #incluir el campo para colocar el nombre 8080
        nombreTexto = "Nombre: "
        dibujoFormato.text((14, 22), nombreTexto,
                           font=tituloFont, fill=(0, 0, 0))

    if(ifecha == True):
            #incluir el campo para colocar el nombre 8080
            fechaTexto = "Fecha: "
            dibujoFormato.text((400, 22), fechaTexto, 
                               font=tituloFont, fill=(0, 0, 0))
    
    
    if(icarnet == True):
            #incluir el campo para colocar el nombre 8080
            nA, nL = dibujoFormato.textsize(nombreTexto, font=tituloFont)
            carnetTexto = "Carnet: "
            dibujoFormato.text((14, (22+nL*1.5)), carnetTexto, 
                               font=tituloFont, fill=(0, 0, 0))
    
    if(imateria == True):
            #incluir el campo para colocar el nombre 8080
            nA, nL = dibujoFormato.textsize(nombreTexto, font=tituloFont)
            materiaTexto = "Materia: "
            dibujoFormato.text((400, (22+nL*1.5)), materiaTexto, 
                               font=tituloFont, fill=(0, 0, 0))
    
    par = 0
    if final-inicio == 0:
        par = 0
    else:
        if ((final+1)-inicio)%2 == 0:
            par = 1
        else:
            par = 0
        
    for i in range(inicio, final+1, 2):
        pdf.add_page()
        
        identificadorTexto = str(i)
        fname = "IMG%.3d.png" % i
        dibujoFormato.text((509, 419), identificadorTexto,
                               font=numeroFont, fill=(0, 0, 0))
        img_superior = fname.format(os.getpid())
        formato.save(img_superior)
        pdf.image(img_superior, x=30, y=20, w=160, h=120)
        os.remove(img_superior)
        
        dibujoFormato.rectangle((509, 419, 540, 450), fill=(255, 255, 255))
        
        if i == final and par == 0:
            break
        
        identificadorTexto_b = str(i+1)
        fname_b = "IMG%.3d.png" % (i+1)
        dibujoFormato.text((509, 419), identificadorTexto_b,
                               font=numeroFont, fill=(0, 0, 0))
        img_inferior = fname_b.format(os.getpid())
        formato.save(img_inferior)
        pdf.image(img_inferior, x=30, y=146, w=160, h=120) 
        os.remove(img_inferior)
        
        dibujoFormato.rectangle((509, 419, 540, 450), fill=(255, 255, 255))
    
    pdf.output(salida)
    return 1