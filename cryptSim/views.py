from flask import flash, redirect, render_template, request, url_for

from cryptSim.forms import MovimientoForm
import locale
from . import app

from .models import RUTADB, DBManager, Movimiento, ListaMovimientos, formatear_numeros

@app.route('/')
def home():

    db=DBManager(RUTADB)
    lista = ListaMovimientos()
    lista.cargar_movimientos()

    locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')

    for movimiento in lista.movimientos:
        for clave in movimiento:
            if movimiento[clave]!='EUR' and (clave=='cantidad' or clave=='precio_unitario' or clave=='cantidad_divisa_destino'):
                movimiento[clave]=formatear_numeros(movimiento[clave])

    return render_template('inicio.html', movs=lista.movimientos)

@app.route('/nuevo_movimiento', methods=['GET', 'POST'])
def nuevo_movimiento():
    if request.method == 'GET':
        movimiento= {}
        formulario = MovimientoForm(data=movimiento)
        return render_template('form_movimiento.html', form=formulario, id=movimiento.get('id'))

    if request.method == 'POST':
        db = DBManager(RUTADB)
        
        formulario = MovimientoForm(data=request.form)
        lista = ListaMovimientos()
        lista.cargar_movimientos()

        if formulario.validate():
            mov_dict = {
                'divisa_origen': formulario.divisa_origen.data,
                'cantidad': float(formulario.cantidad.data),
                'divisa_destino': formulario.divisa_destino.data
            }

            if mov_dict['divisa_origen']!=mov_dict['divisa_destino']:

                lista.actualizar_lista_total_invertido_por_divisas()

                if mov_dict['cantidad']<lista.lista_total_por_divisa[f'{mov_dict['divisa_origen']}'] or mov_dict['divisa_origen']=='EUR':

                    movimiento = Movimiento(mov_dict)

                    db.agregar_movimiento(movimiento)

                    flash('¡Movimiento registrado correctamente!','success')
                
                    return redirect(url_for('home'))
            
                elif mov_dict['cantidad']>=lista.lista_total_por_divisa[f'{mov_dict['divisa_origen']}'] and mov_dict['divisa_origen']!='EUR':

                    flash('No dispones de la cantidad suficiente de divisa para realizar la operación. Por favor, inténtalo de nuevo.', 'error')
                
                    return render_template('form_movimiento.html', form=formulario)

                else: 
                    return render_template('form_movimiento.html', form=formulario)
                
            elif mov_dict['divisa_origen']==mov_dict['divisa_destino']:
                    
                flash('La divisa origen y la divisa destino son la misma. Por favor, inténtalo de nuevo.')
                return render_template('form_movimiento.html', form=formulario)

    return redirect(url_for('home'))

@app.route('/estado_inversion')
def estado_inversion():

    lista = ListaMovimientos()
    lista.cargar_movimientos()
    lista.valor_inversion_euros()


    locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
    total_euros_invertidos = locale.currency(abs(lista.total_euros_invertidos), grouping=True)
    estado_inversion_euros = locale.currency(lista.estado_inversion_euros, grouping=True)
    total_actual = locale.currency((lista.estado_inversion_euros-abs(lista.total_euros_invertidos)), grouping=True)


    return render_template('estado_inversion.html', euros_actual=estado_inversion_euros, euros_invertidos=total_euros_invertidos, total_actual=total_actual)
