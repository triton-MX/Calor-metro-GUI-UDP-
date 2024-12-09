# -*- coding: utf-8 -*-
"""
Created on Nov 20th 2024

@author: Triton Perea
"""
# Importar librerias a usar
import numpy as np, pandas as pd     #Numpy y pandas para manejo de datos
import matplotlib.pyplot as plt  # 3 librearias para graficas 
import time as tm                #time para marcar tiempos de ejecucion
import threading as th, queue as qu   #threading para manejo de hilos
import sys
import socket as sk          # socket para recibir datos por UDP
import os

# Función que divide cadena de caracteres cada ','
def separarDatos(busDatos):
    """
    Separa una cadena de texto en una lista de elementos, usando la coma como delimitador.

    Parameters
    ----------
    busDatos : str
        Cadena de texto que contiene los datos separados por comas.

    Returns
    -------
    listaDatos : list
        Lista de elementos separados por comas.
    """
    listaDatos= busDatos.split(",")
    return listaDatos

""" Funciones relativas a la funcionalidad 
-------------------------------------------------------------------------------
"""
class Recibir:
    """
    Clase para recibir datos utilizando el protocolo UDP.

    Atributos:
    ----------
    reference : object
        Referencia al objeto principal que maneja la interfaz gráfica.
    data_queue : queue.Queue
        Cola para pasar los datos a la interfaz gráfica.
    data_queue_0 : queue.Queue
        Cola para pasar los datos entre las clases de recepción y registro.
    UDP_IP : str
        Dirección IP del dispositivo desde el que se reciben los datos. Por defecto "192.168.1.64".
    port : int
        Puerto UDP a utilizar. Por defecto 8889.
    """
    def __init__(self,reference, data_queue, data_queue_0, UDP_IP= "192.168.1.64",port=8889):
        """
        Inicializa la clase de recepción de datos.

        Parameters
        ----------
        reference : object
            Referencia al objeto principal de la interfaz gráfica.
        data_queue : queue.Queue
            Cola para pasar los datos a la interfaz gráfica.
        data_queue_0 : queue.Queue
            Cola para pasar los datos entre clases.
        UDP_IP : str, opcional
            Dirección IP del dispositivo de recepción. Por defecto es "192.168.1.64".
        port : int, opcional
            Puerto UDP a utilizar. Por defecto es 8889.
        """
        # Variables globales
        self.reference = reference      # Paso la referencia del root principal
        self.data_queue = data_queue    # Usar la cola pasada desde la InterfazGrafica
        self.data_queue_0 = data_queue_0    #Cola para datos entre clases de recibir y registro
        self.UDP_IP, self.port= UDP_IP, port
        self.is_recieving = False       # Ayuda a gestionar el hilo en segundo plano
        self.sock = sk.socket(sk.AF_INET,sk.SOCK_DGRAM) # Vincular el socket a todas las interfaces locales
        self.ver= Verificador()

    def recibirDatos(self):
        """
        Método para recibir datos usando el protocolo UDP.

        Este método escucha en el puerto definido, recibe los datos y los pasa a la cola
        para su posterior procesamiento.

        Returns
        -------
        None.
        """
        try:
            self.sock.setsockopt(sk.SOL_SOCKET, sk.SO_REUSEADDR, 1)
            self.sock.bind(('',self.port))         #sock.bind(('',SHARED_UDP_PORT))sock.bind((UDP_IP, UDP_PORT))
            print(f"Servidor UDP escuchando en el puerto {self.port}")
        except sk.error as e:
            print(f"Error al intentar vincular el socket: {e}")
            sys.exit(1)
            
        self.is_recieving = True        # Cambia la variable booleana para indicar que si se estan recibiendo datos
        while self.is_recieving:        # Mientras se sigan recibiendo datos
            #print("intento")
            try:
                data, addr = self.sock.recvfrom(1024)   # Recibe datos desde el objeto sock
                try:
                    print(f"Mensaje recibido de {addr}: {data.decode()}")
                    data_point = data.decode().strip()     # Decodifica los datos recibidos
                    Xdata=self.ver.verificarRecepcion(data_point) # Manda los datos a verificar y guardar
                    self.data_queue_0.put(Xdata)         # Se pasa el mensaje a la cola
                except ValueError as ve:
                    print(f"Error al convertir datos a float: {ve}")
            except Exception as e:
                        print(f"Error recibiendo datos: {e}")

    def detenerRecepcion(self):
        """
        Detiene la recepción de datos y cierra el socket.

        Returns
        -------
        None.
        """
        self.is_recieving = False   # Detiene el bucle de recepción
        
        if hasattr(self, 'sock') and self.sock:
            try:
                self.sock.close()
                print("Socket cerrado correctamente.")
            except Exception as e:
                print(f"Error al cerrar el socket: {e}")

class Verificador:
    """
    Clase encargada de verificar la recepción de los datos y asegurarse de que sean válidos.

    Atributos:
    ----------
    len_temp : int
        Longitud esperada para los datos recibidos.
    Tdata : str
        Variable para almacenar el dato verificado.
    verificador_0 : str
        Primer carácter que debe aparecer al inicio del dato.
    verificador_1 : str
        Primer carácter que debe aparecer al final del dato.
    """
    def __init__(self, len_temp=5):
        """
        Inicializa el objeto Verificador.

        Parameters
        ----------
        len_temp : int, opcional
            Longitud esperada para los datos. El valor por defecto es 5.
        """
        self.len_temp= len_temp
        self.Tdata = "0"
        self.verificador_0, self.verificador_1= "x", "y"
        self.data_queue_0 = qu.Queue()    #Cola para transferencia de datos entre clases
    
    def verificarRecepcion(self, data_point):
        """
        Verifica que el mensaje recibido esté completo y sea válido.

        Parameters
        ----------
        data_point : str
            El dato recibido para ser verificado.

        Returns
        -------
        str
            El dato verificado si es válido, o "0" si el dato es inválido.
        """
        temp_data= str(data_point)[1:-1]         #Para pasar al DF se retiran el encabezado y el final
        
        # Se verifica mensaje completo con la letra x, al inicio y al final
        if data_point[0]==self.verificador_0 and data_point[-1]==self.verificador_1 and len(temp_data)==self.len_temp:
            print("Mensaje completo\n")
            print(temp_data)
            self.Tdata=temp_data
        else:
            print("Warning: Mensaje incompleto")
            print(temp_data)
            # Reiniciar el DataFrame a ceros con el mismo número de columnas y los índices correspondientes
            self.Tdata="0"
              
        
        print(f"\n {self.Tdata} \n")
        
        return self.Tdata

# ----------------------------------------------------------------------------
class Registro:
    """
    Clase para el registro y almacenamiento de los datos recibidos en un archivo CSV.

    Atributos:
    ----------
    data_queue : queue.Queue
        Cola de datos para el almacenamiento.
    data_queue_0 : queue.Queue
        Cola para el intercambio de datos entre las clases.
    men_queue : queue.Queue
        Cola para los mensajes del sistema.
    isWriting : bool
        Bandera para determinar si se está escribiendo datos.
    ruta_csv : str
        Ruta del archivo CSV donde se almacenarán los datos.
    flag_inter : bool
        Bandera de interrupción del proceso de registro.
    contador : int
        Contador para los datos procesados.
    data_register : pd.DataFrame
        DataFrame donde se almacenan los datos temporales.
    """
    def __init__(self, isWriting, data_queue, data_queue_0, men_queue):
        """
        Inicializa la clase de registro de datos.

        Parameters
        ----------
        isWriting : bool
            Bandera para determinar si se deben escribir los datos.
        data_queue : queue.Queue
            Cola para el almacenamiento de los datos.
        data_queue_0 : queue.Queue
            Cola para pasar los datos entre clases.
        men_queue : queue.Queue
            Cola para manejar los mensajes.
        """
        # Variables Globales
        self.data_queue= data_queue
        self.data_queue_0 = data_queue_0
        self.men_queue = men_queue
        self.isWriting = isWriting
        self.ruta_csv = r"C:\..."           # Ruta absoluta a donde se desea guardar. Personalizar
        self.flag_inter = False
        self.contador=0                 #
        self.data_register= pd.DataFrame()
        self.ver=Verificador()
        self.buffer = pd.DataFrame()
        
    # Evento: registrar datos de vuelo en una hoja de calculo
    def registrarDatos(self): 
        """
        Método para registrar los datos en un archivo CSV.

        Este método recibe los datos de la cola, los procesa y los almacena en un archivo CSV
        cada 3600 datos. También se encarga de actualizar la interfaz con mensajes de estado.

        Returns
        -------
        None.
        """
        self.contador=0                 #
        self.men_queue.put("Datos incompletos")
        
        while self.isWriting:
            try:
                data_point = self.data_queue_0.get()  # Timeout para evitar bloqueo indefinido
                
                # Decodificar y procesar el data_point
                #data= self.ver.verificarRecepcion(self, data_point)
                Ddata = pd.DataFrame([data_point])
                     # Dividir la cadena en una lista
#Ajustar numero de datos a recibir                
                if self.contador<3600:
                    self.data_register= pd.concat([self.data_register, Ddata], ignore_index=True)
                    self.contador += 1  # Incrementar el contador
                else:
                    #Graficar cada 3600 datos. En este caso, se recibe un dato cada 0.5 seg.
                    self.data_queue.put(self.data_register)
                    self.men_queue.put("Datos completos")
                    # Guardar informacion en .csv cada 3600 datos. *estimado cada 30 minutos de recepcion
                    self.data_register.to_csv(self.ruta_csv, mode='a', index=False, header=not os.path.exists(self.ruta_csv))
                    self.data_register=pd.DataFrame() #Reiniciar el Data Frame vacio
                    self.contador=0     #Reiniciar contador
                    
            except self.data_queue_0.Empty:
                continue
            
    def detenerRegistro(self):
        """
        Detiene el proceso de registro de datos y guarda la información acumulada en un archivo CSV.

        Este método interrumpe el proceso de escritura en el archivo CSV y guarda cualquier dato
        pendiente en el DataFrame en el archivo correspondiente. Si el registro es interrumpido antes
        de completar el ciclo de 3600 datos, se guarda la información registrada hasta ese momento.

        Returns
        -------
        None
        """
        self.isWriting = False 
        # Guardar informacion en .csv si se interrumpe el registro. *estimado cada 30 minutos de recepcion
        if not self.data_register.empty:
            self.data_register.to_csv(self.ruta_csv, mode='a', index=False, header=not os.path.exists(self.ruta_csv))
        self.data_register=pd.DataFrame() #Reiniciar el Data Frame vacio
        self.contador=0     #Reiniciar contador
        