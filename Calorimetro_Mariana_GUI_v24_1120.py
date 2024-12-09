# -*- coding: utf-8 -*-
"""
Created on Nov 20th 2024

@author: Triton Perea

Este programa implementa una interfaz gráfica en Python para la recepción, registro, 
procesamiento y visualización de datos provenientes de un sistema UDP. 
Integra funcionalidades con CustomTkinter y Matplotlib, permitiendo 
manejar gráficos en tiempo real y controlar múltiples procesos mediante hilos.

"""
# Paqueterías a usar
import tkinter as tk
from tkinter import ttk    #tkinter para Interfaz grafica
import customtkinter as ctk      # Para mejorar la interfaz
import matplotlib.pyplot as plt  # 3 librearias para graficas 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import numpy as np, pandas as pd     #Numpy y pandas para manejo de datos
import time as tm                #time para marcar tiempos de ejecucion
import threading as th, queue as qu  #threading para manejo de hilos
import sys, io
import Calorimetro_Mariana_receiverUDP_v24_1120 as rc
import Calorimetro_Mariana_senderUDP_v24_1120 as sd


"""Interfaz grafica
-----------------------------------------------------------------------------"""
class InterfazGrafica:
    """
   Clase que gestiona la interfaz gráfica para la recepción, registro y visualización
   de datos provenientes de un sistema UDP. Integra gráficos en tiempo real y permite
   controlar el flujo de datos mediante botones y menús.

   Atributos:
   ----------
   root : tkinter.Tk
       Ventana principal de la aplicación.
   data_queue : queue.Queue
       Cola para recibir los datos procesados.
   data_queue_0 : queue.Queue
       Cola para manejar datos intermedios.
   men_queue : queue.Queue
       Cola para mensajes entre hilos.
   data_dict : dict
       Diccionario para almacenar datos recibidos.
   xs, ys : list
       Listas para almacenar datos de los ejes X e Y en los gráficos.
   isReceiving, isSending, isWriting : bool
       Bandera para controlar el estado de recepción, envío y registro.
   recibir : Calorimetro_Mariana_receiverUDP_v24_1120.Recibir
       Instancia de la clase que gestiona la recepción de datos.
   registro : Calorimetro_Mariana_receiverUDP_v24_1120.Registro
       Instancia de la clase que gestiona el registro de datos.
   enviar : Calorimetro_Mariana_senderUDP_v24_1120.sender
       Instancia de la clase que gestiona el envío de datos.
   """
    def __init__(self, root):
        """
        Constructor que inicializa la ventana principal y todos los elementos 
        gráficos, colas y objetos relacionados con el manejo de datos.

        Parámetros:
        -----------
        root : tkinter.Tk
            Ventana principal de la aplicación.
        """
        self.root=root
        self.root.geometry("800x600")
        self.root.title("Interfaz grafica de recepcion de datos")
        
        # Establecer modo de apariencia (claro, oscuro o sistema)
        ctk.set_appearance_mode("Dark")  # Tema Dark
        ctk.set_default_color_theme("blue")  # Tema azul moderno
        
        # Variables globales
        self.isReceiving= False
        self.isSending= False
        self.isWriting= False
        self.data_queue = qu.Queue()    #Cola para recibir los datos
        self.data_queue_0 = qu.Queue()  #Cola para manejo de datos intermedios
        self.men_queue = qu.Queue()     #Cola para indicar si se consiguieron los registros necesarios
        self.data_dict = {'Temperatura': []}
        self.xs, self.ys= [],[]
        
        #Crear instancia de las clases provenientes de receiverUDP
        self.recibir =rc.Recibir(self, self.data_queue, self.data_queue_0)  
        self.registro= rc.Registro(self, self.data_queue, self.data_queue_0, self.men_queue)     # Registrar      
        self.enviar = sd.sender(self)   #Crear instancia de la clase proveniente de senderUDP
        
        # Configuración de la interfaz gráfica
        self._crearElementosGraficos()
        
    def _crearElementosGraficos(self):
        """
        Método privado para crear los elementos gráficos principales: marcos, botones,
        gráficos y cuadros de texto.
        """        
        # Crear una barra de menú personalizada con CustomTkinter
        self.menu_frame = ctk.CTkFrame(self.root, bg_color='OldLace')
        self.menu_frame.place(relx=0, rely=0, relwidth=1, relheight=0.08)

        #Cuadro izquierdo
        self.frameLeft = ctk.CTkFrame(self.root, corner_radius=15)
        self.frameLeft.place(relx=0,rely=0.1,relwidth=0.7,relheight=0.9)
        
        #Cuadro izquierdo superior
        self.frameLeft1 = ctk.CTkFrame(self.frameLeft, bg_color='grey')
        self.frameLeft1.place(relx=0, rely=0, relwidth=1, relheight=0)
        
        #Cuadro izquierdo inferior
        self.frameLeft2 = ctk.CTkFrame(self.frameLeft, bg_color='grey')
        self.frameLeft2.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        #Cuadro derecho
        self.frameRight = ctk.CTkFrame(self.root, corner_radius=15, bg_color='#1E7387')
        self.frameRight.place(relx=0.7,rely=0.1,relwidth=0.3,relheight=0.9)
        
        #Titulo de cuadro de vuelo
        self.subtitle1 = ctk.CTkLabel(self.frameRight, text="Consola", font=('Verdana',10)).pack(padx=10, pady=10)
        
        #Grafica 1
        self.canvas1, self.scatter, self.ax = self.crearGrafica("C vs T") 
        self.canvas1.draw()
        
        # Botones en la barra de menú
        self._crearBotonesMenu()
        
        # Consola de salida
        self._crearConsola()

        
    def _crearBotonesMenu(self):
        """
        Crea los botones en la barra de menú superior para controlar las operaciones
        de recepción, registro y simulación de datos.
        """
        self.button0 = ctk.CTkButton(self.menu_frame, text="Iniciar escucha",fg_color="#676969", hover_color="gray", command=self.iniciarRecepcion).pack(side="left", padx=10)
        self.button1 = ctk.CTkButton(self.menu_frame, text = "Iniciar registro", command=self.iniciarRegistro).pack(side="left",padx=10)
        self.button2 = ctk.CTkButton(self.menu_frame, text = "Iniciar simluación", command=self.iniciarEnvio).pack(side="left",padx=10)
        self.button3 = ctk.CTkButton(self.menu_frame, text="Detener escucha", command=self.detenerRecepcion).pack(side="left", padx=10)
        self.button4 = ctk.CTkButton(self.menu_frame, text="Detener registro", command=self.detenerRegistro).pack(side="left", padx=10)
        self.button5 = ctk.CTkButton(self.menu_frame, text="Detener simulacion", command=self.detenerEnvio).pack(side="left", padx=10)
        self.button6 = ctk.CTkButton(self.menu_frame, text="Apagar y salir", fg_color="#676969", hover_color="gray",command=self.apagar).pack(side="right", pady=10)
        
    def _crearConsola(self):
        """
        Configura un widget de texto para redirigir y mostrar la salida de consola
        dentro de la interfaz gráfica.
        """
        # Crear un widget scrolledtext (Text con barra de desplazamiento) en frameRight
        self.text_out = ctk.CTkTextbox(self.frameRight)
        self.text_out.pack(side='left', expand=True, fill="both", pady=10)
        self.scrollbar = ctk.CTkScrollbar(self.frameRight, orientation="vertical", command=self.text_out.yview)
        self.scrollbar.pack(side="right", fill="y")
        # Enlazar el scrollbar con el text_out y hacer el textbox de solo lectura
        self.text_out.configure(yscrollcommand=self.scrollbar.set)
        self.text_out.configure(state="disabled")
        # Redirigir sys.stdout para capturar la salida de la consola
        self.stdout_backup = sys.stdout  # Guardar la referencia al stdout original
        sys.stdout = TextRedirector(self.text_out, "stdout")  # Redirigir stdout a Text widget
        # Etiqueta inferior de la interfaz
        self.etiqueta = ctk.CTkLabel(root, text="")
        self.etiqueta.pack(side=tk.BOTTOM)
        self.etiqueta.pack(fill=tk.X) 

    # Creacion de graficas -----------------------------------------------
    def actualizarPuntos(self):
        """
        Actualiza los datos del gráfico de dispersión con los nuevos puntos 
        obtenidos de las colas de datos y mensajes.
    
        El método verifica si hay datos disponibles en las colas y actualiza 
        las coordenadas y valores de color en el gráfico. Además, configura 
        etiquetas y título del gráfico.
    
        Returns
        -------
        None.
        """
        datos_temp= []
        datos_c=[]
        try:
            mensaje = self.men_queue.get_nowait()
            
            if mensaje == "Datos completos":
                
                datos_temp= self.data_queue.get()
                datos_c= self.calculoCalor()
                
                self.scatter.set_offsets(list(zip(datos_temp,datos_c)))
                self.scatter.set_array(np.array(datos_temp)) # Dado que cmap depende de datos_temp
                
                # Volver a dibujar el grafico con los nuevos puntos        
                self.ax.set_title("Scatter")
                self.ax.set_xlabel('Eje X')
                self.ax.set_ylabel('Eje Y')
                self.canvas1.draw()
                
                # Reiniciar el ciclo de recepcion
                self.men_queue.put("Mensaje incompleto")
                return              # Salir del bucle tras terminar de actualizar la grafica
                
        except qu.Empty:
            print("Sin mensajes recibidos aun")
            
        except Exception as e:
            print(f"Error inesperado: {e}")
                 
    def calculoCalor(self): # Calor aplicado
        """
        Returns
        -------
        None.

        """
        intensidad = 0.569  # Amperaje del sistema
        resistencia = 1.4   # Valor de la resistencia en el circuito
        delta_t = 0.5       # Diferencia de tiempo entre mediciones
        
        q = pow(intensidad, 2)*resistencia*delta_t
        
        datos_c = [q for _ in range(3600)]
        
        return datos_c
    
    def crearGrafica(self, titulo):
        """
        Crea un gráfico vacío para ser actualizado dinámicamente.

        Parámetros:
        -----------
        titulo : str
            Título del gráfico.

        Retorna:
        --------
        FigureCanvasTkAgg, matplotlib.scatter, matplotlib.axes:
            Objeto gráfico y sus elementos para manipulación posterior.
        """
        fig, ax = plt.subplots(facecolor="0.55", figsize=(10,8), dpi=100)
        ax.set_xlim(0, 100)     # Limite eje x 
        ax.set_ylim(-5, 5)     # Limite eje y 
        ax.set_title(titulo, color='red', size=16, family="Tahoma")
        ax.set_xlabel("Temperatura")
        ax.set_ylabel("Calor")
        
        # Crear grafico scatter vacio
        scatter= ax.scatter( [], [], cmap='viridis')     #Inicialmente vacia
        
        grafica = FigureCanvasTkAgg(fig, master=self.frameLeft2)
        grafica.get_tk_widget().pack()
        
        return grafica, scatter, ax
    
    """ Funciones relativas a widgets de la interfaz grafica 
    ---------------------------------------------------------------------------
    """
    def iniciarRecepcion(self):
        """
        Inicia el proceso de recepción de datos a través del puerto UDP.
        
        Este método lanza un hilo que gestiona la recepción de paquetes de datos 
        en tiempo real, asegurando que la interfaz gráfica no se bloquee 
        durante este proceso.

        Notas:
        ------
        - La bandera `isReceiving` se activa para evitar múltiples inicios.
        - Los datos recibidos se encolan en `data_queue` para procesamiento posterior.
        """
        self.etiqueta.configure(text="Se inicia recepcion de datos")
        if not self.isReceiving:
            self.isReceiving= True
            self.thread_Reciv = th.Thread(target=self.recibir.recibirDatos)
            self.thread_Reciv.start()
            
    def detenerRecepcion(self):
        """
        Detiene el proceso de recepción de datos.

        Cambia la bandera `isReceiving` a `False` para finalizar el hilo asociado 
        a la recepción de paquetes. Esto asegura que no se sigan procesando datos entrantes.
        """
        self.recibir.detenerRecepcion()
        if self.isReceiving:
            self.isReceiving= False
            if hasattr(self, 'thread_Reciv') and self.thread_Reciv.is_alive():
                self.thread_Reciv.join(1)     # Esperar a que el hilo de envio termine, si existe
            self.etiqueta.configure(text="Se detiene recepcion de datos")
                    
    def iniciarRegistro(self):
        """
        Inicia el registro de datos recibidos en un archivo CSV.

        Este método lanza un hilo para registrar continuamente los datos encolados 
        en `data_queue_0`, permitiendo almacenamiento persistente en tiempo real.
        """
        self.etiqueta.configure(text="Se inicia registro de datos")
        if not self.isWriting:
            self.isWriting= True
            self.thread_Reg = th.Thread(target=self.registro.registrarDatos)
            self.thread_Reg.start()
            self.after= self.root.after(100, self.actualizarPuntos)  # Llama a la función cada 100 ms
    
    def detenerRegistro(self):
        """
        Detiene el registro de datos en el archivo.

        Cambia la bandera `isWriting` a `False`, finalizando el hilo responsable 
        de escribir datos en el archivo CSV.
        """
        self.registro.detenerRegistro()
        if self.isWriting:
            self.isWriting=False
            if hasattr(self, 'thread_Reg') and self.thread_Reg.is_alive():
                self.thread_Reg.join(1)          # Esperar a que el hilo de recepcion termine, si existe
            if hasattr(self, 'after'):
                self.root.after_cancel(self.after)
            self.etiqueta.configure(text= "Se detiene el registro de datos")
            
    def iniciarEnvio(self):
        """
       Inicia el envío de datos simulados al puerto UDP.

       Este método lanza un hilo para enviar paquetes de datos simulados en 
       intervalos definidos, útil para pruebas o depuración del sistema.
       """
        self.etiqueta.configure(text="Se inicia envio de datos. Se usan datos de simulador")
        if not self.isSending:
            self.isSending = True
            self.thread_Send = th.Thread(target=self.enviar.send)
            self.thread_Send.start()
    
    def detenerEnvio(self):
        """
        Detiene el envío de datos simulados.

        Cambia la bandera `isSending` a `False`, finalizando el hilo responsable 
        de generar y enviar paquetes simulados.
        """
        self.enviar.detenerEnvio()
        if self.isSending:
            self.isSending=False
            if hasattr(self, 'thread_Send') and self.thread_Send.is_alive():
                self.thread_Send.join(1)     # Esperar a que el hilo de envio termine, si existe
            self.etiqueta.configure(text="Se detiene envio de datos")
 
    # Funcion para limpiar un frame
    def clearFrame(frame):
        # destroy all widgets from frame
        for widget in frame.winfo_children():
            widget.destroy()
    
    # Evento: cerrar el programa
    def apagar(self):
        """
        Cierra la aplicación de manera segura.

        Este método limpia los recursos utilizados, detiene los hilos activos 
        y cierra la ventana principal para finalizar la ejecución del programa.
        """
        self.detenerRecepcion()
        self.detenerRegistro()
        self.detenerEnvio()

        tm.sleep(1) 
        sys.stdout = sys.__stdout__
        root.destroy()
        root.quit()
        print("Proceso finalizado")


# Clase que redirige stdout al widget Text
class TextRedirector(io.StringIO):
    """
    Clase auxiliar para redirigir la salida estándar de la consola a un widget de texto.

    Atributos:
    ----------
    widget : tkinter.Text
        Widget donde se mostrará la salida redirigida.
    tag : str
        Etiqueta asociada al tipo de salida ('stdout' o 'stderr').

    Métodos:
    --------
    write:
        Escribe el texto redirigido en el widget.
    flush:
        Mantiene la compatibilidad con el flujo estándar.
    """
    def __init__(self, widget, tag=None):
        """
        Constructor que inicializa el redireccionamiento.

        Parámetros:
        -----------
        widget : tkinter.Text
            Widget donde se mostrará la salida redirigida.
        tag : str
            Etiqueta asociada al tipo de salida ('stdout' o 'stderr').
        """
        super().__init__()
        self.widget = widget
        self.tag = tag

    def write(self, string):
        """
        Escribe una cadena de texto en el widget.

        Parámetros:
        -----------
        string : str
            Texto que será escrito en el widget.
        """
        if self.widget.winfo_exists():
            self.widget.configure(state="normal")
            self.widget.insert(tk.END, string)  # Insertar texto en el widget Text
            self.widget.see(tk.END)  # Desplazarse automáticamente hacia el final del texto
            self.widget.configure(state="disabled")
        else:
            sys.stdout = sys.__stdout__

    def flush(self):
        """
        Mantiene la compatibilidad con el flujo estándar. Este método no realiza ninguna operación.
        """
        pass  # No necesitamos hacer nada para flush en este caso

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    root = ctk.CTk()  # Crear la ventana principal con customtkinter
    app = InterfazGrafica(root)
    
    root.mainloop()