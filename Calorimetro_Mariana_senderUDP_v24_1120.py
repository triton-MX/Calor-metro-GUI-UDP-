# -*- coding: utf-8 -*-
"""
Created on Nov 26th 2024

@author: Triton Perea
"""
# Importar librerias a usar
import random
import socket as sk
import pandas as pd
import time

""" SENDER UDP
----------------------------------------------------------------------------"""
class sender:
    """
    Clase para enviar datos a través de UDP. 
    Simula datos o los carga desde un archivo CSV y los envía a una dirección y puerto específicos.

    Attributes
    ----------
    opcion : str
        Método de simulación a utilizar ("simuladorCSV" o "simuladorRandom").
    simular : simuladorExperimento
        Instancia de la clase `simuladorExperimento` para generar los datos.
    UDP_IP : str
        Dirección IP del receptor de los datos.
    UDP_PORT : int
        Puerto UDP del receptor de los datos.
    num_test : str
        Cadena que representa el dato actual a enviar.
    isSending : bool
        Indica si el envío de datos está activo.
    n : int
        Número de datos a enviar.
    """
    def __init__(self,isSending= False, opcion='simuladorCSV' , UDP_IP="192.168.1.66", UDP_PORT=8889, n=5000):
        """
        Inicializa el objeto Sender con los parámetros dados.

        Parameters
        ----------
        isSending : bool, optional
            Indica si el envío de datos está activo al iniciar. Default: False.
        opcion : str, optional
            Método de simulación a usar ("simuladorCSV" o "simuladorRandom"). Default: 'simuladorCSV'.
        UDP_IP : str, optional
            Dirección IP del receptor. Default: "192.168.1.66".
        UDP_PORT : int, optional
            Puerto UDP del receptor. Default: 8889.
        n : int, optional
            Número de datos a enviar. Default: 5000.
        
        """
        self.opcion=opcion
        self.simular = simuladorExperimento(n)
        self.UDP_IP, self.UDP_PORT= UDP_IP, UDP_PORT
        self.num_test=""
        self.isSending = isSending
        self.n= n
        
    def send(self):
        """
        Envía datos a través del protocolo UDP utilizando el método de simulación especificado.
        Si la opción no es válida, muestra un mensaje de error.
        """
        while self.isSending:
            sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
            metodo= getattr(self.simular, self.opcion, None)
            if callable(metodo):
                dataset= metodo()
                for i, num_test in enumerate(dataset):
                    try:
                      sock.sendto(bytes(num_test, "utf-8"), (self.UDP_IP, self.UDP_PORT))
                      #print("UDP IP:", self.UDP_IP)
                      #print("UDP puerto:", self.UDP_PORT)
                      print("Mensaje enviado:", num_test, "\n")
                      time.sleep(0.5)

                      if i>=self.n-1:
                        break
                    except Exception as e:
                        print(f"Error al enviar: {e}")
                        pass 
            else:
                print(f"Error: la simulacion{self.tipo} no esta definida")
            
            sock.close()
            
    def detenerEnvio(self):
        """
        Detiene el envío de datos.
        """
        self.is_sending = False

class simuladorExperimento:
    """
    Clase para simular experimentos y generar datos aleatorios o cargar datos desde un archivo CSV.

    Attributes
    ----------
    is_sending : bool
        Indica si se están generando datos para envío.
    repeticiones : int
        Número de datos a generar.
    """
    def __init__(self, n, is_sending=True):
        """
        Inicializa la clase con el número de datos a generar.

        Parameters
        ----------
        n : int
            Número de datos a generar.
        is_sending : bool, optional
            Indica si la simulación está activa. Default: True.
        """
        self.is_sending=is_sending
        self.repeticiones= n
        
    
    def simuladorRandom(self): #-----------------------------------------------------
        """
        Genera datos aleatorios en el formato 'x00.00y', donde:
        - 'x': Identificador inicial del dato.
        - '00.00': Temperatura registrada por el sensor (valor aleatorio).
        - 'y': Identificador final del dato.

        Returns
        -------
        list
            Lista de cadenas representando los datos generados.
        """
        mu= 50  #Media (valor central)
        sigma=5 #Desviacion estandar
        
        dataset=[]
        
        for i in range(self.repeticiones):
            num_random=[]           #Lista vacia
            num_random.append('x')  # en el algoritmo, el x sirve para verificar inicio 
        
            # Generar un numero flotante aleatorio de 4 digitos, 2 antes del punto y 2 despues
            digit = round(random.gauss(mu,sigma),2)     #Redondear a 2 decimales
            num_random.append(str(digit))               #Convertir a cadena de texto y concatenarlo
                
            num_random.append('y')   # se agrega el ultimo digito de la cadena para verificar si llega completo el dato
        
            # Concatenar lista en cadena
            num_test = ''.join(num_random)
            
            dataset.append(num_test)
            
        print(f"\n-------------------- \n Enviar:{dataset}")
        
        return dataset
    
    # Importar datos de archivo CSV
    def simuladorCSV(self):
        """
        Carga datos desde un archivo CSV y los convierte al formato 'x<data>y'.

        Returns
        -------
        list
            Lista de cadenas representando los datos cargados.
        """
        ruta_csv=r"C:\Users\iapcl\Documents\BioC\DatosEmulador.csv"
        data = pd.read_csv(ruta_csv, header=None)
        dataset= ["x"+str(valor[0])+"y" for valor in data.values]
        
        #print(f"\n-------------------- \n Enviar:{dataset}")
        
        return dataset
    