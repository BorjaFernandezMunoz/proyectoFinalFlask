from datetime import datetime
import locale
import os
import sqlite3

from flask import app

import requests


RUTADB = 'cryptSim/data/movimientosCryptSim.db'

apikey = '8C7855D2-637B-45D6-A953-E83C0AF8DC8C' #'tu-clave-coinapi'
# apikey = '60f21295-81aa-42cf-9d0b-c7b4d5c5d9cf' la de cumon

server = 'http://rest.coinapi.io'

endpoint = '/v1/exchangerate'

headers = {'X-CoinAPI-Key': apikey}


def extraer_rate_de_coinapi(divisa_origen, divisa_destino):
    """
    Función que utilizamos para extraer el ratio entre la divisa de origen y la divisa de destino en distintos momentos del programa.
    """
    coinapi_url = server + endpoint + '/' + divisa_origen + '/' + divisa_destino

    response = requests.get(coinapi_url, headers=headers)

    if response.status_code == 200:

        exchange = response.json()
        rate = exchange.get('rate', 0)
        
        return rate

    else:

        mensaje = 'Error en la conversión.'
        return mensaje        
     
def formatear_numeros(numero):
    """
    Función que utilizamos para darles a los números el formato español.
    """
    locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
    
    str_numero= str(numero)

    if '.' in str_numero:

        str_numero=f'{locale.format_string("%.6f", numero, grouping=True)} €'
 
    else: 
        str_numero=locale.currency(numero, grouping=True)   

    return str_numero

class DBManager:
    """
    Clase que permite interactuar con la base de datos.
    """
    def __init__(self, ruta):

        if not os.path.exists(ruta):

            conexion = sqlite3.connect(ruta)
            cursor = conexion.cursor()

            cursor.execute('''CREATE TABLE "movimientosCryptSim" ( 
                            "id"	INTEGER NOT NULL UNIQUE,
                            "fecha"	TEXT NOT NULL,
                            "hora" TEXT NOT NULL,
                            "divisa_origen" TEXT NOT NULL, 
                            "cantidad" NUMERIC NOT NULL, 
                            "divisa_destino" TEXT NOT NULL,
                            "precio_unitario"	NUMERIC NOT NULL,
                            "cantidad_divisa_destino"	NUMERIC NOT NULL, 
                            PRIMARY KEY("id" AUTOINCREMENT))''')
            
        
            self.ruta = ruta

        else:

            self.ruta = ruta

    def consultarSQL(self, consulta):

        conexion = sqlite3.connect(self.ruta)
        cursor = conexion.cursor()
        cursor.execute(consulta)
        datos = cursor.fetchall()

        self.registros = []
        nombres_columna = []

        for columna in cursor.description: 
            nombres_columna.append(columna[0])


        for dato in datos:
            movimiento = {}
            indice = 0
            for nombre in nombres_columna:
                movimiento[nombre] = dato[indice]
                indice += 1
            self.registros.append(movimiento)

        conexion.close()

        return self.registros

    def actualizarMovimiento(self, movimiento):

        conexion = sqlite3.connect(self.ruta)
        cursor = conexion.cursor()
        sql = 'UPDATE movimientos SET fecha=?, hora=?, desde=?, cantidad=?, a=?, precio unitario =? WHERE id=?'

        resultado = -1

        try:
            params = (
                movimiento.fecha,
                movimiento.hora,
                movimiento.divisa_origen,
                movimiento.cantidad,
                movimiento.divisa_destino,
                movimiento.precio_unitario,
            )
            cursor.execute(sql, params)
            conexion.commit()
            resultado = cursor.rowcount

        except Exception as ex:
            conexion.rollback()

        conexion.close()
        return resultado
    
    def agregar_movimiento(self, movimiento):

        conexion = sqlite3.connect(self.ruta)
        cursor = conexion.cursor()
        sql = 'INSERT INTO movimientosCryptSim(fecha, hora, divisa_origen, cantidad, divisa_destino, precio_unitario, cantidad_divisa_destino) VALUES (?, ?, ?, ?, ?, ?, ?)'
        val = (movimiento.fecha, movimiento.hora, movimiento.divisa_origen, movimiento.cantidad, movimiento.divisa_destino, movimiento.precio_unitario, movimiento.cantidad_divisa_destino)
        cursor.execute(sql, val)
        conexion.commit()

class Movimiento:

    """
    Clase para instanciar los movimientos o conversiones realizadas. 

    """

    def __init__(self, dict_mov):

        self.divisa_origen = dict_mov.get('divisa_origen', '')
        self.cantidad = dict_mov.get('cantidad', 0)
        self.divisa_destino = dict_mov.get('divisa_destino', '')
        
        self.rate = extraer_rate_de_coinapi(self.divisa_origen, self.divisa_destino)

        self.precio_unitario = 1/(self.rate)
        self.cantidad_divisa_destino = float(self.cantidad) * self.rate

        fecha_hora = datetime.now()


        self.fecha = (fecha_hora.date()).strftime("%d-%m-%Y")
        self.hora = (fecha_hora.now()).strftime("%H:%M:%S")

    def __str__(self):
        return f'De {self.cantidad} {self.divisa_origen} a {self.cantidad_divisa_destino} {self.divisa_destino}'


    def __repr__(self):
        return self.__str__()
    
class ListaMovimientos:
    """
    Clase que nos permite instanciar la lista de movimientos guardada en la base de datos, con sus atributos y métodos propios.
    """
    def __init__(self):

        try:
            self.cargar_movimientos()
        except:
            self.movimientos = []

        self.lista_total_por_divisa = {'EUR':0,'BTC':0,'ETH':0,'USDT':0,'ADA':0,'SOL':0,'XRP':0, 'DOT':0, 'DOGE':0,'SHIB':0}
        self.estado_inversion_euros= self.valor_inversion_euros()
        self.total_euros_invertidos= self.total_por_divisa('EUR')

    def __str__(self):
        result = ''
        for mov in self.movimientos:
            result += f'\n{mov}'
        return result
    
    def __repr__(self):
        return self.__str__()
    

    def cargar_movimientos(self):

        db = DBManager(RUTADB)

        sql = 'SELECT fecha, hora, divisa_origen, cantidad, divisa_destino, precio_unitario,cantidad_divisa_destino FROM movimientosCryptSim'

        datos = db.consultarSQL(sql)

        self.movimientos = []

        for dato in datos:
            self.movimientos.append(dato)

        return self.movimientos
    
    def inversion_recuperada(self, divisa):
        """
        Recorre los movimientos realizados, y si hay alguna inversión en alguna divisa concreta, se suma al total disponible de esa divisa.
        """
        for movimiento in self.movimientos:

            if divisa == movimiento['divisa_destino']:
                self.lista_total_por_divisa[divisa] = self.lista_total_por_divisa[divisa] + movimiento['cantidad_divisa_destino']

        return self.lista_total_por_divisa[divisa]
        
    def inversion_realizada(self, divisa):
        """
        Recorre los movimientos realizados, y si hay algún gasto en una divisa concreta, se resta al total disponible de esa divisa.
        """
        for movimiento in self.movimientos:

            if divisa == movimiento['divisa_origen']:
                self.lista_total_por_divisa[divisa] = self.lista_total_por_divisa[divisa] - movimiento['cantidad'] 

        return self.lista_total_por_divisa[divisa]
        
    def actualizar_lista_total_invertido_por_divisas(self):
        """
        Recorre el diccionario 'lista_total_por_divisa' y actualiza la cantidad de divisas que se poseen.
        """
        
        self.lista_total_por_divisa = {'EUR':0,'BTC':0,'ETH':0,'USDT':0,'ADA':0,'SOL':0,'XRP':0, 'DOT':0, 'DOGE':0,'SHIB':0}

        for clave in self.lista_total_por_divisa:

            self.inversion_recuperada(clave)
            self.inversion_realizada(clave)

        return self.lista_total_por_divisa
        
    def total_por_divisa(self, divisa):
        """
        Devuelve el total de una divisa concreta.
        """
        self.actualizar_lista_total_invertido_por_divisas()
        return self.lista_total_por_divisa[divisa]        


    def valor_inversion_euros(self):
        """
        Recorre la lista de totales por divisa, conecta con Coinapi y transforma el valor actual de las divisas acumuladas en euros.
        """ 
        self.actualizar_lista_total_invertido_por_divisas()
        total_euros = 0
        for clave in self.lista_total_por_divisa:
            if clave != 'EUR':
                rate = extraer_rate_de_coinapi(clave, 'EUR')
                equivalencia_en_euros = self.lista_total_por_divisa[clave] * rate
                total_euros = total_euros + equivalencia_en_euros

        return total_euros
    

# TODO: en views, en la página de simulación de movimiento, ordenarla tal y como se presenta en el pdf. 
# Hay que mostrar la cantidad que se puede adquirir de la divisa destino cuando se pulsa la calculadora; cuando se pulsa la calculadora
# aparece la cantidad y se activa el botón de validar.

# TODO: investigar cómo confirmar. Cuando se le da al botón de la calculadora, nos puede redirigir a otra página donde el botón de confirmar está ya activo.

# TODO: cuestiones estilísticas.
