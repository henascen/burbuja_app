#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 23 10:59:13 2020

"""
import sys
PY3 = sys.version_info[0] == 3

if PY3:
    xrange = range

#Importar librerias y modulos necesarios para procesar la imagen y datos

#Necesaria para crear la vista frontal de la foto del examen
from imutils.perspective import four_point_transform
#Necesaria para crear una lista de los contornos encontrados en la imagen
from imutils import contours
#Modulos necesarios para el procesamiento
import numpy as np
import imutils
import cv2
import pytesseract

#############################################################################
#Se utilizan funciones obtenidas del archivo squares.py en el repositorio de 
# opencv, estas pueden aplicarse para detectar cuadrados dentro de una imagen, 
#el cálculo del coseno se dejó sin modificación unicamente se modificó 
#find_squares() en la función detectar_examen -> find_boxes()

#https://github.com/opencv/opencv/blob/master/samples/python/squares.py
##############################################################################

#Devuelve únicamente los contornos que representan las opciones de respuesta
def encontrar_opciones(contornos, caja_longitud, caja_relacion, contornos_preguntas):
    #contornos -- array con todos los contornos que están dentro del examen
    #caja_longitud -- supuesta medida que debe de tener al menos el rectángulo
    #                que cubre al contorno de la opcion de respuesta (burbuja)
    #caja_relacion -- modificador de la proporción que debe de tener el
    #                rectángulo que cubre a la burbuja. Idealmente debe ser lo
    #                más cercano a 1, pero tras prueba y error se verificó
    #                que ampliar el rango permitía detectar todos los contornos
    #contornos_preguntas -- array donde se guardaron los contornos que
    #                 corresponden exclusivamente a las burbujas
    
    #Se recorre cada contorno encontrado uno por uno
    for c in contornos:
        #Se calcula la caja que encierra los contornos (w-width, h-heigth), 
        # utilizamos esos valores para calcular la proporcion de aspecto (ar)
        (x, y, w, h) = cv2.boundingRect(c)
        ar = w / float(h)
 
        #Para poder ser considerado como burbuja, el contorno debe de ser lo 
        # suficientemente ancho y largo, y tener una proporcion de aspecto de 
        # por lo menos 1, cuando no se detectan todos los contornos se hace
        # una modificación a los límites para obtener todos los contornos
        if w >= caja_longitud and h >= caja_longitud and ar >= 0.9-caja_relacion and ar <= 1.1+caja_relacion:
            #Si el contorno cumple con las medidas establecidas, se agrega
            # al array que contiene solo a los contornos de las burbujas
            contornos_preguntas.append(c)
    
    #Se devuelve el array que se ha llenado con los contornos que cumplen los
    # límites
    return contornos_preguntas

#Devuelve la nota que se obtiene al comparar las respuestas correctas con las
# respuestas de un examen a calificar, a partir de estas comparaciones se
# decide dibujar contornos sobre las opciones según sean correctas (verdes) o
# incorrectas (rojas). Solamente se manejan los contornos de las opciones 
# marcadas correctamente
def obtener_nota(respuestas_correctas, respuestas_electas, contornos, exam_vistaplanta):
    #respuestas_correctas -- array con las respuestas correctas
    #respuestas_electas -- array con las respuestas a calificar
    #contornos -- lista con los contornos de las respuestas marcadas, para las
    #               respuestas no válidas se pasa el primer contorno de los 4
    #exam_vistaplanta -- imagen del examen sobre el cual se dibujan los contornos
    #               y que es la obtenida de la extracción de la foto
    
    #Se inicializa el contador de respuestas correctas
    correctas = 0
    
    #Se inicializan los puntos de partida para los contornos, esto debido a que
    # no siguen la misma correlación que las respuesta y los indices en los 
    # búcles no se corresponden. Se hace uno para cada fila (hay 10 filas con 
    # 4 contornos de las 4 respuestas marcadas para cada pregunta). Los contornos
    # están guardados del 0 al 4 de las preguntas 1, 11, 21, 31 por ejemplo y
    # así consecutivamente
    pf_contorno = 0
    sf_contorno = 4
    tf_contorno = 8
    cf_contorno = 12
    qf_contorno = 16
    ssf_contorno = 20
    spf_contorno = 24
    of_contorno = 28
    nf_contorno = 32
    df_contorno = 36
    
    #Se recorre cada grupo de contornos con sus respectivas respuestas asociadas
    # el for está diseñado para incrementar en 10 unidades simulando las posiciones
    # de las preguntas en el formato predefinido del examen. Luego para cada
    # uno se compara si la respuesta es correcta o no, si lo es no se dibuja
    # el contorno porque se hará cuando se procese la imagen al extraer las
    # respuestas marcadas. Sin embargo cuando sea incorrecta se dibujará el
    # contorno de color rojo de la opción marcada en el examen. EN cada bucle
    # se incrementa el número de correctas si es el caso para hacer un recuento
    # general y obtener la nota final.
    for ipf in range(0, 31, 10):
        #Incrementamos de 10 en 10 para acceder a cada respuesta que 
        # corresponde a cada pregunta de la fila (1, 10, 11, 31 todos menos 1
        # para hacer coincidir con el indice dentro del array)
        if respuestas_electas[ipf] == respuestas_correctas[ipf]:
            correctas += 1
        else:
            #Si no es correcta se verifica que no cumpla con un valor específico,
            # aunque está comparación no tiene efecto en la versión final se había 
            # pensado para un escenario distinto
            if np.any(contornos[ipf] != 4):  
                cv2.drawContours(exam_vistaplanta, [contornos[pf_contorno]], -1, (20,20,200), 2) 
        #Incrementamos el indice que elige el contorno a dibujar, los contornos 
        # siguen el orden de las filas de izquierda a derecha, los primeros 4 
        # contornos del array [contornos] son los 4 de la primera fila del examen
        pf_contorno += 1
    for isf in range(1, 32, 10):
        if respuestas_correctas[isf] == respuestas_electas[isf]:
            correctas += 1
        else:
            if np.any(contornos[isf] != 4):  
                cv2.drawContours(exam_vistaplanta, [contornos[sf_contorno]], -1, (20,20,200), 2)    
        sf_contorno += 1
    for itf in range(2, 33, 10):
        if respuestas_electas[itf] == respuestas_correctas[itf]:
            correctas += 1
        else:
            if np.any(contornos[itf] != 4):  
                cv2.drawContours(exam_vistaplanta, [contornos[tf_contorno]], -1, (20,20,200), 2)    
        tf_contorno += 1 
    for icf in range(3, 34, 10):
        if respuestas_correctas[icf] == respuestas_electas[icf]:
            correctas += 1
        else:
            if np.any(contornos[icf] != 4):  
                cv2.drawContours(exam_vistaplanta, [contornos[cf_contorno]], -1, (20,20,200), 2)    
        cf_contorno += 1
    for iqf in range(4, 35, 10):
        if respuestas_correctas[iqf] == respuestas_electas[iqf]:
            correctas += 1
        else:
            if np.any(contornos[iqf] != 4):  
                cv2.drawContours(exam_vistaplanta, [contornos[qf_contorno]], -1, (20,20,200), 2)    
        qf_contorno += 1
    for issf in range(5, 36, 10):
        if respuestas_correctas[issf] == respuestas_electas[issf]:
            correctas += 1
        else:
            if np.any(contornos[issf] != 4):  
                cv2.drawContours(exam_vistaplanta, [contornos[ssf_contorno]], -1, (20,20,200), 2)    
        ssf_contorno += 1
    for ispf in range(6, 37, 10):
        if respuestas_correctas[ispf] == respuestas_electas[ispf]:
            correctas += 1
        else:
            if np.any(contornos[ispf] != 4):  
                cv2.drawContours(exam_vistaplanta, [contornos[spf_contorno]], -1, (20,20,200), 2)    
        spf_contorno += 1
    for iof in range(7, 38, 10):
        if respuestas_correctas[iof] == respuestas_electas[iof]:
            correctas += 1
        else:
            if np.any(contornos[iof] != 4):  
                cv2.drawContours(exam_vistaplanta, [contornos[of_contorno]], -1, (20,20,200), 2)    
        of_contorno += 1
    for inf in range(8, 39, 10):
        if respuestas_correctas[inf] == respuestas_electas[inf]:
            correctas += 1
        else:
            if np.any(contornos[inf] != 4):  
                cv2.drawContours(exam_vistaplanta, [contornos[nf_contorno]], -1, (20,20,200), 2)    
        nf_contorno += 1
    for idf in range(9, 40, 10):
        if respuestas_correctas[idf] == respuestas_electas[idf]:
            correctas += 1
        else:
            if np.any(contornos[idf] != 4):  
                cv2.drawContours(exam_vistaplanta, [contornos[df_contorno]], -1, (20,20,200), 2)    
        df_contorno += 1
    
    #Cada pregunta vale igual por lo que se calcula la nota con una fórmula
    # simple luego de acumularlas en un solo contador
    nota = correctas/4
    
    #Se devuelve el valor de la nota y la imagen con los contornos dibujados
    return nota, exam_vistaplanta

#Se abre una ventana de openCV para mostrar la imagen que se pase como 
# parámetro junto con el titulo respectivo
def mostrar_imagen(titulo, imagen):
    #Mostrar la imagen obtenida
    cv2.imshow(titulo, imagen)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

#Se abre una ventana de openCV para mostrar la imagen que está en la
# ruta que se pase como parámetro junto con el titulo respectivo    
def mostrar_imagen_ruta(titulo, filename):
    imagen = cv2.imread(filename)
    #Se le aplica a la imagen la detección de página (recuadro más grande 
    # después del contorno de la imagen)
    examen, area_examen = detectar_examen(imagen)
    #Mostrar la imagen obtenida
    cv2.imshow(titulo, examen)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

#Se devuelve la imagen del examen sin el fondo (considerando que es de color 
# muy distinto al fondo y que es el elemento principal de la foto) visto desde
# una perspectiva de planta. Además se pasa el área que tiene el contorno que 
# lo rodea
def detectar_examen(imagen):
    #imagen -- foto tomada al examen leída con imread-opencv
    
    #Funciones obtenidas del repositorio de openCV para detectar cuadros en 
    # la imagen
    def angle_cos(p0, p1, p2):
        d1, d2 = (p0-p1).astype('float'), (p2-p1).astype('float')
        return abs( np.dot(d1, d2) / np.sqrt( np.dot(d1, d1)*np.dot(d2, d2) ) )


    def find_boxes(img):
        img = cv2.GaussianBlur(img, (5, 5), 0)
        squares = []
        for gray in cv2.split(img):
            for thrs in xrange(0, 255, 26):
                if thrs == 0:
                    bin = cv2.Canny(gray, 0, 50, apertureSize=5)
                    bin = cv2.dilate(bin, None)
                else:
                    _retval, bin = cv2.threshold(gray, thrs, 255, cv2.THRESH_BINARY)
                cntours, _hierarchy = cv2.findContours(bin, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
                for cnt in cntours:
                    cnt_len = cv2.arcLength(cnt, True)
                    cnt = cv2.approxPolyDP(cnt, 0.02*cnt_len, True)
                    #Esta comparación es diferente con respecto a la que utiliza
                    # el 
                    if len(cnt) == 4 and cv2.contourArea(cnt) > 1000 and cv2.isContourConvex(cnt):
                        cnt = cnt.reshape(-1, 2)
                        max_cos = np.max([angle_cos( cnt[i], cnt[(i+1) % 4], cnt[(i+2) % 4] ) for i in xrange(4)])
                        if max_cos < 0.1:
                            squares.append(cnt)
                                
        return squares
    
    #Se redimensiona la imagen para un procesamiento más rápido y eficiente
    examen = imutils.resize(imagen, width=700)
    #Se encuentran los recuadros de la imagen, se convierte a un numpy array
    # y finalmente se ordenan según el área que ocupan en orden ascendente
    recuadros = find_boxes(examen)
    recuadros = np.array(recuadros)
    recuadros = sorted(recuadros, key=cv2.contourArea, reverse=True)
    
    #Se convierte la imagen a escala de grises
    examensub = cv2.cvtColor(examen, cv2.COLOR_BGR2GRAY)
    #Se aplica umbralización a la imagen para intentar dejar la página en 
    # blanco con clara distinción al fondo que lo rodea
    examensub = cv2.threshold(examensub, 250, 255, 
                                     cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    
    #Se inicializa variable para guardar el indice que corresponde al recuadro
    # del examen solamente (que contiene a la página)
    indice_vp = 0
    #Se recorre el ciclo según la cantidad de contornos obtenidos (esto para
    # abarcarlos a todos en el análisis)
    for i in range(len(recuadros)):
        #Se sustraen los contornos y se utiliza la función de imutils para 
        # obtener la imagen que nos da la vista de planta de la imagen
        examen_vp = four_point_transform(examensub, recuadros[i].reshape(4,2))
        #Se guarda el ancho y largo de la imagen
        height, width = examen_vp.shape[:2]
        #Se inicializan las variables que guardan el valor de los pixeles a 
        # analizar
        pixel_xi = 0
        pixel_xd = 0
        pixel_ya = 0
        pixel_yb = 0
        
        #Se recorre según la altura a todos los pixeles en x y se suman en la
        # variable respectiva, (se coloca el punto de análisis 5 pixeles a la
        # derecha del origen y 5 antes del ancho total para mejor análisis). 
        # Los pixeles solo pueden tener valores de 0 y 1 y así se iran sumando
        for p in range(height):
            pixel_xi = pixel_xi + examen_vp[p, 5]
            pixel_xd = pixel_xd + examen_vp[p, width-5]
        
        #Se repite lo anterior pero para el ancho de la imagen, siempre dejando
        # un margen respectivo
        for p in range(width):
            pixel_ya = pixel_ya + examen_vp[5, p]
            pixel_yb = pixel_yb + examen_vp[height-5, p]
        
        #Para que la imagen sea la del examen los pixeles analizados tienen que
        # sumar 0 ya que todos serían blancos al ser parte de la papeleta de 
        # ese color y que con la umbralización permaneción así distinto al fondo
        # que se convirtió a negro. Si todos los pixeles en el margen analizado 
        # tanto en altura como en anchura suman 0 entonces se guarda el indice
        # porque es el del examen
        if pixel_xi == 0 and pixel_xd == 0 and pixel_ya == 0 and pixel_yb == 0:
            indice_vp = i
            break
    
    #Con el indice encontrado se extrae el área del contorno respectivo, y 
    # además se obtiene el examen extraído con ese contorno visto desde planta
    area = cv2.contourArea(recuadros[indice_vp])
    examen = four_point_transform(examen, recuadros[indice_vp].reshape(4,2))
    
    #Se devuelve la imagen del examen extraído y el área obtenida
    return examen, area

#Devuelve el recuadro inferior del formato del examen luego de detectarlo y
# el área de la misma. Se ocupan las funciones de squares.py pero se le hace
# una modificación para limitar las áreas a detectar (tienen que ser menores
# a la del examen encontrado)
def detectar_cinfo(examen, areac):
    #examen -- imagen con la perspectiva de planta aplicada del examen
    #areac -- área del contorno que rodea al examen unicamente
    
    def angle_cos(p0, p1, p2):
        d1, d2 = (p0-p1).astype('float'), (p2-p1).astype('float')
        return abs( np.dot(d1, d2) / np.sqrt( np.dot(d1, d1)*np.dot(d2, d2) ) )


    def find_boxes(img):
        img = cv2.GaussianBlur(img, (5, 5), 0)
        squares = []
        for gray in cv2.split(img):
            for thrs in xrange(0, 255, 26):
                if thrs == 0:
                    bin = cv2.Canny(gray, 0, 50, apertureSize=5)
                    bin = cv2.dilate(bin, None)
                else:
                    _retval, bin = cv2.threshold(gray, thrs, 255, cv2.THRESH_BINARY)
                cntours, _hierarchy = cv2.findContours(bin, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
                for cnt in cntours:
                    cnt_len = cv2.arcLength(cnt, True)
                    cnt = cv2.approxPolyDP(cnt, 0.02*cnt_len, True)
                    #Se detectan los recuadros solo si son menores al área del 
                    # contorno del examen y mayores que un mínimo
                    if len(cnt) == 4 and cv2.contourArea(cnt) > 1000 and cv2.contourArea(cnt) < areac and cv2.isContourConvex(cnt):
                        cnt = cnt.reshape(-1, 2)
                        max_cos = np.max([angle_cos( cnt[i], cnt[(i+1) % 4], cnt[(i+2) % 4] ) for i in xrange(4)])
                        if max_cos < 0.1:
                            squares.append(cnt)
                                
        return squares
    
    #Se aplica la función para encontrar los recuadros dentro del examen y
    # se convierte a un numpy array
    recuadros = find_boxes(examen)
    recuadros = np.array(recuadros)
    #Se ordenan los recuadros encontrados en orden descendente (el más pequeño
    # primero)
    recuadros = sorted(recuadros, key=cv2.contourArea, reverse=False)
    #De acuerdo al formato utilizado el más pequeño según los criterios de 
    # detección sería el recuadro inferior donde está el número de papeleta
    area = cv2.contourArea(recuadros[0])
    #Se devuelve el listado de recuadros ordenado y el área del primer
    # recuadro (el que importa)
    return recuadros, area

def leer_respuestas(exam_vistaplanta):
    # exam_vistaplanta --> imagen vista desde la perspectiva de planta
    
    #Se inicializa la lista que guardará los contornos que se pasaran a la 
    # comparación de correcta o incorrecta
    contornos_comparar = []
    #Se inicializa una lista que guarda los contornos a dibujar dentro de 
    # esta funció
    contorno_dibujar = []
    #Se inicializa el numpy array que guarda las respuestas leídas del examen
    respuestasGuardadas = np.zeros((40,1))
    
    #Se transformá la vista de planta a una escala de grises
    exam_vistaplantaGris = cv2.cvtColor(exam_vistaplanta, cv2.COLOR_BGR2GRAY)
    #Se aplica umbralización al examen en escala de gris y se guarda solo la
    #imagen
    exam_umbralizado = cv2.threshold(exam_vistaplantaGris, 0, 255, 
                             cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    
    #Se extraen los contornos encontrados en el examen umbralizados, pero
    # unicamente los que se encuentran más externos dentro del recuadro
    contornos = cv2.findContours(exam_umbralizado.copy(), cv2.RETR_EXTERNAL, 
                              cv2.CHAIN_APPROX_SIMPLE)
    #Se extrae unicamente el array con los contornos 
    contornos = imutils.grab_contours(contornos)
    
    #Se inicializan  los parámetros utilizados para identificar los 
    # contornos que serán considerado burbujas
    caja_longitud = 12
    caja_relacion = 0.01
    #Se inicializa el array que guardará los contornos de las burbujas
    contornos_preguntas = []
    #Se obtienen los contornos de las burbujas utilizando la función 
    # respectiva antes definida
    contornos_preguntas = encontrar_opciones(contornos, caja_longitud, caja_relacion, contornos_preguntas)
    
    #Se comprueba si hay 160 burbujas (esto debido a que se conoce el número
    # fijo de opciones y de preguntas) mientras no se cumpla se deberán 
    # modificar los valores de los parámetros para ampliar o reducir el rango
    # que identifica los contornos como burbujas
    while len(contornos_preguntas) != 160:
        #Se determina si hay menos burbujas de las que deberían
        if len(contornos_preguntas) < 160:
            #Por prueba y error se encontró que es debido a la proporción de
            # aspecto, por lo que se amplia el rango que permite
            caja_relacion += 0.05
            #Se vacía la lista ya que se encontrarán los nuevos contornos
            contornos_preguntas = []
            contornos_preguntas = encontrar_opciones(contornos, caja_longitud, caja_relacion, contornos_preguntas)
        #Se determina si hay más burbujas de las que deberían
        if len(contornos_preguntas) > 160:
            #Por prueba y error se determinó que modificando el tamaño que se
            # permite de la caja alrededor se discriminaban otras formas
            caja_longitud += 1
            contornos_preguntas = []
            contornos_preguntas = encontrar_opciones(contornos, caja_longitud, caja_relacion, contornos_preguntas)
    
    #Cuando se cumple la condición de encontrar 160 contornos (en principio
    # todas burbujas) se organizan con la función sort_contours de imutils, 
    # esto nos permite tenerlas en la lista de la más superior hasta la más
    # inferior
    contornos_preguntas, cajas_preguntas = contours.sort_contours(contornos_preguntas, 
                                                method="top-to-bottom")
   
    #Se crea un array que va de 0 hasta el número de contornos de burbujas,
    # pero hace saltos cada 16 números. Por ejemplo: [0, 16, 32....]
    # luego se enumera cada elemento de 0 hasta el total de filas que
    # existen y finalmente se recorre cada elemento
    for (q, i) in enumerate(np.arange(0, len(contornos_preguntas), 16)):
    	#Se enlistan los contornos por cada fila principal, es decir por cada
        # iteración se hace un grupo de 16 contornos según la fila 
        # correspondiente (hay 10 filas según el formato establecido), esta 
        # lista ordena a las burbujas de la misma fila de izquierda a derecha
        contornos = contours.sort_contours(contornos_preguntas[i:i + 16])[0]
        #Modificamos el valor de q para que vaya concuerde con el número de
        # pregunta real y no el indice del array
        q += 1
        #Se separa de la lista de 16 los que van a cada pregunta, es decir a 
        # grupos de 4, y al estar ordenados de izquierda a derecha se sabe que
        # cada 4 será una pregunta distinta
        for (d, e) in enumerate(np.arange(0, len(contornos), 4)):
            #Recorremos los grupos de 4 para obtener de forma individual cada
            # contorno en cada iteracion
            
            #Si ya pasamos el primer grupo modificamos q para que concuerde de
            # nuevo con el número de pregunta real (en cada fila van cada 10, 
            # por ejemplo: 1, 11, 21, 31)
            if d > 0:
                q += 10
            
            #Se inicializa el indicador que nos ayudará a saber si ya se ha
            # marcado una burbuja en la pregunta
            indicada = 0
            #Se inicializa el array que guardará momentaneamente las 4
            # burbujas de la pregunta actual
            respuestasObtenidas = np.zeros((4,1))
            
            #Se guardan los cuatros contornos de la pregunta
            contorno_dibujar = contornos[e:e+4]
            #Se crea la variable para indicar que contorno se ha marcado
            contornoM = np.zeros((4,1))
            #Se inicializa una variable para guardar indicador si se tienen
            # múltiples respuestas contestadas en una pregunta
            multiples = 0
            #Se enumera cada elemento de los 4 contornos de burbujas en la
            # pregunta, de manera que se van a recorrer solo las burbujas 
            # que corresponden a una sola pregunta
            for (j, c) in enumerate(contornos[e:e+4]):
                #Se construye una mascara para que solo revele en binario la
                # burbuja en cuestion, está tendrá la misma forma que la 
                # imagen del examen umbralizado
                mascara = np.zeros(exam_umbralizado.shape, dtype="uint8")
                #Se dibuja el contorno de la burbuja en la máscara
                cv2.drawContours(mascara, [c], -1, 255, -1)
                
                #Aplicamos la mascara a la imagen umbralizada con una
                # operación AND, de manera que solo quede la burbuja actual 
                # ya que sería lo único que abarcaría la máscarra. Luego se
                # cuenta el numero de los pixeles que no son cero en la imagen
                # obtenida luego de aplicar la máscara.
                mascara = cv2.bitwise_and(exam_umbralizado,exam_umbralizado,mask=mascara)
                total = cv2.countNonZero(mascara)
                
                #Guardamos el valor de los pixeles que no son cero en el array
                # de las respuestas obtenidas
                respuestasObtenidas[j] = total
                                
                #Si hemos llegado a la última burbuja de la pregunta
                if j == 3:
                    #Se calcula el umbral para considerar la burbuja marcada,
                    # esto se hace promediando el valor de los pixeles que no
                    # son cero de las 4 burbujas. 
                    umbralMarcada = np.mean(respuestasObtenidas)
                    #Se inicializa la variable que servirá como referencia al
                    # indice de la respuesta respectiva.
                    # Las respuestas = (0:A, 1:B, 2:C, 3:D)
                    respuesta = 0
                    #Se recorre cada elemento de las respuestas obtenidas, es
                    # decir que se va por cada valor de los pixeles que no son
                    # cero para cada burbuja
                    for k in np.nditer(respuestasObtenidas):
                        #Si es mayor que el umbral y no se ha encontrado otra
                        # respuesta marcada se guarda la respuesta según 
                        # corresponda, además se indica que ya hay una burbuja
                        # marcada
                        if k > umbralMarcada+6 and indicada == 0:
                            respuestasGuardadas[q-1] = respuesta
                            indicada = 1
                            contornoM[respuesta] = 1
                        #Sino, si es mayor que el umbral pero ya se ha marcado
                        # una respuesta anteriormente se declara la respuesta
                        # como nula (valor de 4) por lo tanto se va a tomar
                        # como incorrecta en la calificación
                        elif k > umbralMarcada+5 and indicada == 1:
                            respuestasGuardadas[q-1] = 4
                            contornoM[respuesta] = 1
                            multiples += 1
                        #Sino, si se llega a la última opción y no se ha reconocido
                        # que se ha marcado alguna se declara nula (4) y se dice que
                        # multiples es 4 como indicador del vacío
                        elif respuesta == 3 and indicada == 0:
                            respuestasGuardadas[q-1] = 4
                            multiples = 4
                        #Se incrementa el indicador de la clave de respuesta
                        respuesta += 1
                    
                    #Si la respuesta se considero nula
                    if respuestasGuardadas[q-1] == 4:
                        #Guardar el primero contorno de los cuatro solo para cumplir 
                        # con el formato de la lista
                        contornos_comparar.append(contorno_dibujar[0])
                        #Si multiples está entre 1 y 3
                        if multiples > 0 and multiples < 4:
                            #Para cada contorno enumerado
                            for xy, contorno_marcado in enumerate(contornos[e:e+4]):
                                #Si el indice en cuestión corresponde a un contorno marcado
                                if contornoM[xy] == 1:
                                    #Dibujar el contorno de la opción marcada
                                    cv2.drawContours(exam_vistaplanta, contorno_marcado, -1, (20,20,200), 2)
                        #Sino si, ha sido una respuesta nula de tipo vacía        
                        elif multiples == 4:
                            #Dibujar los últimos 3 contornos en rojo (el primero se ha pasado
                            # al principio y se dibujará cuando se comparen las respuestas)
                            cv2.drawContours(exam_vistaplanta, contornos[e+1:e+4], -1, (20,20,200), 2)
                    #Si la respuesta es normal que se dibuje verde el contorno según la respuesta
                    # marcada
                    else:
                        contornos_comparar.append(contorno_dibujar[int(respuestasGuardadas[q-1])])
                        cv2.drawContours(exam_vistaplanta, [contorno_dibujar[int(respuestasGuardadas[q-1])]], -1, (0,255,0), 2)
                    
    
    #Se devuelve el array que contiene las respuestas obtenidas del examen,
    # el examen con los contornos dibujados y la lista con los contornos que
    # se deben redibujar luego de la comparación
    return respuestasGuardadas, exam_vistaplanta, contornos_comparar

#Se devuelve la lista de los puntos ordenados en sentido horario comenzando en
# la esquina superior izquierda y terminando en la inferior izquierda. Está 
# basada en la función de imutils de order_points con algunas modificaciones
# para adecuarla a la aplicación
def order_points(pts):
    #pts -- lista con las coordenadas de los puntos 
    
    # se ordenan los puntos basados en su coordenada x
    xSorted = pts[np.argsort(pts[:, 0]), :]
    # se toman los puntos más a la izquierda y más a la derecha según la
    # lista ordenada de la coordenada x
    leftMost = xSorted[:2, :]
    rightMost = xSorted[2:, :]
    # luego se ordenan los puntos según su coordenada y
    # así se puede separar entre los que son más a la izquierda y más
    # a la derecha con su respectiva posición en y
    leftMost = leftMost[np.argsort(leftMost[:, 1]), :]
    #Se obtiene con claridad el izquierdo superior e inferior
    (tl, bl) = leftMost
    #Se obtiene los dos de la derecha pero sin asignar posición en y
    (fr, sr) = rightMost
    
    #Se aplica la distancia city block de cada pixel de la derecha con el punto
    # izquierdo superior
    cityd_1 = (fr[0]-tl[0])+(fr[1]-tl[1])
    cityd_2 = (sr[0]-tl[0])+(sr[1]-tl[1])
    
    #Dependiendo de cual distancia sea más larga así se decide cual es 
    # superior derecho y se guarda en el array
    if cityd_1 > cityd_2:
        puntos = np.array([tl, sr, fr, bl], dtype="float32")
    else:
        puntos = np.array([tl, fr, sr, bl], dtype="float32")
    
    #Se devuelve la lista de puntos ordenados
    return puntos

def procesar_examen(filename):
    #filename -- ruta con la imagen a procesar (foto del examen)
    
    #Leer la imagen dentro de la ruta proporcionada
    examen = cv2.imread(filename)
    #Obtener la vista de planta del examen y el área que ocupa
    examen, area_examen = detectar_examen(examen)
    
    #Extraer las respuestas dentro del examen
    respuestas, examen, contornos_respuestas = leer_respuestas(examen)
    
    #Extraer los recuadros interiores del examen (segun formato)
    recuadros, area_cid = detectar_cinfo(examen, area_examen)
    #Extraer el recuadro inferior y cambiarle la forma
    cuadro_roi = recuadros[0].reshape(4,2)
    #Ordenar el array que contiene la región de interés
    cuadro_roi = order_points(cuadro_roi)
    #Obtener las coordenadas para luego formar un cuadrado alrededor del id
    x1 = int(cuadro_roi[0, 0])
    y1 = int(cuadro_roi[0, 1])
    x2 = int(cuadro_roi[2, 0])
    y2 = int(cuadro_roi[2, 1])
    #Extraer la región donde se encuentra el id (según formato)
    roi = examen[y1+1:y2-2, x1+310:x2-15]
    #Utilizar el pytesseract para obtener el id de la papeleta
    config = ("-l eng --oem 1 --psm 7")
    nid = pytesseract.image_to_string(roi, config=config)
    #Hacer una lista con los caracteres extraídos, y convertir los que no
    # son deseados o con mala lectura a sus valores correctos
    nid = list(nid)
    for cha in range(len(nid)):
        if nid[cha] == '“':
            nid[cha] = '1'
        if nid[cha] == 'B':
            nid[cha] = '8'
        if nid[cha] == "i":
            nid[cha] = '1'
    nid = "".join(nid)
    
    #Ordenar los recuadros en orden ascendente
    recuadros = sorted(recuadros, key=cv2.contourArea, reverse=True)
    
    #Se vacía el cuadro con la roi antes extraída para guardar otra que 
    # corresponda al recuadro superior en el formato
    cuadro_roi = []
    #Se recorren los recuadros
    for cd in recuadros:
        #Se guarda el área del recuadro actual
        area = cv2.contourArea(cd)
        #Si es mayor que el recuadro inferior y menos que la mitad del examen
        if(area > area_cid and area < area_examen/2):
            #Extraer el recuadro
            cuadro_roi = cd
            break
    
    #Cambiarle la forma al recuadro extraído
    cuadro_roi = cuadro_roi.reshape(4,2)
    #Ordenar el array que contiene la región de interés
    cuadro_roi = order_points(cuadro_roi)
    #Obtener las coordenadas para luego formar un cuadrado
    x1 = int(cuadro_roi[0, 0])
    y1 = int(cuadro_roi[0, 1])
    x2 = int(cuadro_roi[2, 0])
    y2 = int(cuadro_roi[2, 1])
    #Extraer la región donde se encuentra la info del examen (según formato)
    roi = examen[y1:y2, x1:x2]
    
    #Se devuelven las respuestas, el id, la imagen del examen, el cuadro superior
    # con la info, y los contornos de las respuestas marcadas extraídas
    return respuestas, nid, examen, roi, contornos_respuestas

