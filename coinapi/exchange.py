from datetime import datetime
import requests


apikey = '60f21295-81aa-42cf-9d0b-c7b4d5c5d9cf'
server = 'http://rest.coinapi.io'
endpoint = '/v1/exchangerate'
headers = {'X-CoinAPI-Key': apikey}


"""
1. Moneda origen (FROM)
2. Moneda destino (TO)
3. Ir API y preguntar el valor de cambio:
        {
        "time": "2017-08-09T14:31:18.3150000Z",
        "asset_id_base": "BTC",
        "asset_id_quote": "USD",
        "rate": 3260.3514321215056208129867667
        }
    3.1 Si hay error: mensaje con los detalles
4. Cantidad de la moneda origen
5. Un XXXX-orig equivale a xxxxx-dest
"""

seguir = 's'

while seguir == 's':
    # vista
    origen = input('¿Qué moneda quieres cambiar? ')
    destino = input('¿Qué moneda quieres obtener? ')
    cantidad = float(input(f'¿Cuantos {origen} quieres gastar? '))
    # /vista

    # modelo
    url = server + endpoint + '/' + origen + '/' + destino

    response = requests.get(url, headers=headers)
    

    if response.status_code == 200:
        # respuesta OK
        exchange = response.json()
        print(exchange)
        rate = exchange.get('rate', 0)
        resultado = cantidad * rate
        # /modelo
        print(f'Un {origen} vale lo mismo que {rate} {destino}')
        print(f'{cantidad} {origen} equivalen a {resultado} {destino}')

        fecha = exchange.get('time', 0)[:-2]

        fecha_hora_reales = datetime.strptime(fecha, "%Y-%m-%dT%H:%M:%S.%f")
        print(fecha_hora_reales)
        fecha = str(fecha_hora_reales.day) +';'+str(fecha_hora_reales.month)+';'+str(fecha_hora_reales.year)
        hora = str(fecha_hora_reales.hour)+':'+str(fecha_hora_reales.minute)+':'+str(fecha_hora_reales.second)
        print(fecha)
        print(hora)

    else:
        # error
        print('Error', response.status_code, ':', response.reason)

    seguir = ''
    while seguir.lower() not in ('s', 'n'):
        seguir = input('¿Quieres consultar de nuevo? (s/n) ').lower()

print('FIN del programa')

# {'time': '2024-12-12T21:34:51.1000000Z', 'asset_id_base': 'EUR', 'asset_id_quote': 'USD', 'rate': 1.048015}