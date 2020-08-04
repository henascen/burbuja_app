#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QFileDialog, QPushButton 
from PyQt5.QtCore import pyqtSignal

from models.primerainterfaz import Ui_MainWindow, Ui_Form_papeleta, Ui_Form_variosExam, Ui_Form_DatosVarios
from models import generarpdf_papeleta, procesador_examenes

import sys

class window_tablaVarios(QtWidgets.QMainWindow):
    trigger = pyqtSignal()
    closing = pyqtSignal()
    def __init__(self, file_respuesta, files_examenes, parent=None):
        super(window_tablaVarios, self).__init__(parent)
        self.ui = Ui_Form_DatosVarios()
        self.ui.setupUi(self)
        self.trigger.connect(self.parent().completar_barra)
        self.closing.connect(self.parent().setup_defecto)
        
        
        self.ui.tableWidget.setColumnCount(5)
        self.ui.tableWidget.setRowCount(2)
        self.ui.tableWidget.setHorizontalHeaderLabels(('ID', 'Datos', 'Nota', 'Calificación', 'Tipo'))
        header = self.ui.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        print(file_respuesta)
        respuestas, nid, examen, datos, contornos_r = procesador_examenes.procesar_examen(file_respuesta)
        nota_r, examen = procesador_examenes.obtener_nota(respuestas, respuestas, contornos_r, examen)        
            
        self.mostrar_respuestas = QPushButton('Mostrar', self)
        self.mostrar_datos = QPushButton('Mostrar', self)
        
        self.ui.tableWidget.setItem(0, 0, QtWidgets.QTableWidgetItem(nid))
        self.ui.tableWidget.setCellWidget(0, 1, self.mostrar_datos)
        self.ui.tableWidget.setItem(0, 2, QtWidgets.QTableWidgetItem("N/A"))
        self.ui.tableWidget.setCellWidget(0, 3, self.mostrar_respuestas)
        self.ui.tableWidget.setItem(0, 4, QtWidgets.QTableWidgetItem("Solución"))
        
        self.btmostrar = []
        self.btdatos = []
        self.imagenes = []
        self.datos = []
        for i in range(len(files_examenes)):
            fila = i+1
            self.btn = QPushButton('Mostrar', self)
            self.btnb = QPushButton('Mostrar', self)
            self.ui.tableWidget.insertRow(fila)
            self.ui.tableWidget.setCellWidget(fila, 1, self.btn)
            self.ui.tableWidget.setCellWidget(fila, 3, self.btnb)
            self.btn.clicked.connect(lambda state, x=i: self.mostrar_respectivo_datos(x))
            self.btnb.clicked.connect(lambda state, x=i: self.mostrar_respectivo(x))
            self.btmostrar.append(self.btn)
            self.btmostrar.append(self.btnb)
            #self.btnsmostrar[i].clicked.connect(lambda: self.mostrar_respectivo(i))
            contestadas, nidb, examenb, datosb, contornos = procesador_examenes.procesar_examen(files_examenes[i])
            self.datos.append(datosb)
            #print(respuestas, contestadas)
            nota, examenb = procesador_examenes.obtener_nota(respuestas, contestadas, contornos, examenb)        
            self.imagenes.append(examenb)
            self.ui.tableWidget.setItem(fila, 0, QtWidgets.QTableWidgetItem(nidb))
            self.ui.tableWidget.setItem(fila, 2, QtWidgets.QTableWidgetItem("{}".format(nota)))
            self.ui.tableWidget.setItem(fila, 4, QtWidgets.QTableWidgetItem("Contestado"))
           
        self.mostrar_respuestas.clicked.connect(lambda: self.ver_respuestas(examen))
        self.mostrar_datos.clicked.connect(lambda: self.ver_datos_respuestas(datos))
        self.trigger.emit()
        
    def ver_respuestas(self, examen):
        procesador_examenes.mostrar_imagen("Respuestas encontradas", examen)
    def ver_datos_respuestas(self, datos):
        procesador_examenes.mostrar_imagen("Datos del examen", datos)
    def mostrar_respectivo(self, num):
        procesador_examenes.mostrar_imagen("Examen del alumno", self.imagenes[num])
    def mostrar_respectivo_datos(self, num):
        procesador_examenes.mostrar_imagen("Info del alumno", self.datos[num])
    def closeEvent(self, event):
        self.closing.emit()
        event.accept()
            
    
class window_variosExam(QtWidgets.QMainWindow):
    fileName = []
    files = []
    def __init__(self, parent=None):
        super(window_variosExam, self).__init__()
        self.ui = Ui_Form_variosExam()
        self.ui.setupUi(self)
        
        self.ui.pushButton_2.setEnabled(False)
        self.ui.pushButton_3.setEnabled(False)
        
        self.ui.pushButton.clicked.connect(self.subir_respuesta)
        self.ui.pushButton_2.clicked.connect(self.subir_examenes)
        self.ui.pushButton_3.clicked.connect(self.calificar_examenes)
    
    def subir_respuesta(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,
            "Abrir foto de respuestas", 
            "Archivo respuestas",
            "Images (*.png *.xpm *.jpg)", options=options)
        if fileName:
            self.fileName = fileName
            self.ui.label_4.setText("Cargado")
            self.ui.pushButton_2.setEnabled(True)
            self.ui.pushButton_3.setEnabled(True)
    
    def subir_examenes(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self,
                            "QFileDialog.getOpenFileNames()",
                            "","Images (*.png *.xpm *.jpg)", options=options)
        if files:
            self.files = files
            self.ui.label_5.setText("Cargado")
            self.ui.progressBar.setEnabled(True)
    
    def calificar_examenes(self):
        self.ui.progressBar.setProperty("value", 86)
        self.sub = window_tablaVarios(self.fileName, self.files, self)
        self.sub.show()
    
    def completar_barra(self):
        self.ui.progressBar.setProperty("value", 100)
    
    def setup_defecto(self):
        self.ui.progressBar.setEnabled(False)
        self.ui.progressBar.setProperty("value", 0)
        self.ui.pushButton_2.setEnabled(False)
        self.ui.pushButton_3.setEnabled(False)
        self.ui.label_4.setText("")
        self.ui.label_5.setText("")
    
class window_papeleta(QWidget):
    def __init__(self):
        super(window_papeleta, self).__init__()
        self.ui = Ui_Form_papeleta()
        self.ui.setupUi(self)
        
        self.ui.spinBox.setMinimum(1)
        self.ui.spinBox_2.setMinimum(1) 
        self.ui.spinBox.valueChanged[int].connect(self.limits)
        
        self.ui.pushButton.clicked.connect(self.generarPDF)
    
    def limits(self):
        self.ui.spinBox_2.setMinimum(self.ui.spinBox.value()) 
        
    def generarPDF(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()","imprimir.pdf","PDF (*.pdf)", options=options)

        self.ui.progressBar.setProperty("value", 50)
        limite_inicial = self.ui.spinBox.value()
        limite_final = self.ui.spinBox_2.value()
        inombre = False
        ifecha = False
        imateria = False
        icarnet = False
        
        if self.ui.checkBox.isChecked() == True:
            inombre = True
        else:
            inombre = False
        if self.ui.checkBox_2.isChecked() == True:
            ifecha = True
        else:
            ifecha = False
        if self.ui.checkBox_3.isChecked() == True:
            imateria = True
        else:
            imateria = False
        if self.ui.checkBox_4.isChecked() == True:
            icarnet = True
        else:
            icarnet = False
        
        formato = "recursos/imagenes/formato.png"
        fuente_titulo = "recuersos/fuentes/monoglyceride.bold.ttf"
        fuente_numero = "recursos/Shahd_Serif.ttf"
        completado = generarpdf_papeleta.generar_pdf(limite_inicial, limite_final, inombre,
                                        ifecha, imateria, icarnet, formato, fuente_titulo, fuente_numero, fileName)
        
        if completado == 1:
            self.ui.progressBar.setProperty("value", 100)
        
class mywindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(mywindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.ui.pushButton.clicked.connect(self.openSub1)
        self.ui.pushButton_3.clicked.connect(self.openSub)
        
    def openSub1(self):
        self.sub = window_variosExam()
        self.sub.show()
    def openSub(self):
        self.sub = window_papeleta()
        self.sub.show()

if __name__ == "__main__":
    def run_app():
        app = QtWidgets.QApplication(sys.argv)
        application = mywindow()
        application.show()
        app.exec_()
    run_app()
