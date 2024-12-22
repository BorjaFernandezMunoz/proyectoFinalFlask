from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    DecimalField,
    SelectField,
    StringField,
    SubmitField
)
from wtforms.validators import DataRequired, NumberRange


class MovimientoForm(FlaskForm):

    fecha = DateField()
    hora = DateField()
    divisa_origen = SelectField(u'Divisa origen', 
                                choices=[('EUR', 'Euro'), ('BTC', 'Bitcoin'), ('ETH', 'Ethereum'), ('USDT','Tether' ), ('ADA', 'Cardano'), 
                                         ('SOL', 'Solana'), ('XRP', 'Ripple'), ('DOT', 'Polkadot'), ('DOGE', 'Dogecoin'), 
                                         ('SHIB', 'Shiba Inu')
                                         ], validators=[
        DataRequired('No has especificado una divisa válida')
    ])



    cantidad = DecimalField('Cantidad a invertir', places=2, validators=[
        DataRequired('No puede haber un movimiento sin una cantidad asociada'),
        NumberRange(
            min=0.1, message='No se permiten cantidades inferiores a 10 centimos')
    ])   
    divisa_destino = SelectField(u'Divisa destino', 
                                choices=[('EUR', 'Euro'), ('BTC', 'Bitcoin'), ('ETH', 'Ethereum'), ('USDT','Tether' ), ('ADA', 'Cardano'), 
                                         ('SOL', 'Solana'), ('XRP', 'Ripple'), ('DOT', 'Polkadot'), ('DOGE', 'Dogecoin'), 
                                         ('SHIB', 'Shiba Inu')
                                         ], validators=[
        DataRequired('No has especificado una divisa válida')
    ])

    submit = SubmitField('Guardar')
