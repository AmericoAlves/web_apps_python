# librerias
from flask import Flask
from flask import render_template
from flask import flash
from flask import request
from flask import jsonify
from flask import Markup

import logging
import io
import os
import sys

import pandas as pd
import numpy as np
import scipy
import pickle

from sklearn.ensemble import GradientBoostingClassifier as GBC



# inicia flask
app=Flask(__name__)



# modelo 
gbc=None


# variables, caracteristicas
var=None
 
    

# para cargar las imagenes
def imagen_vino(color, calidad):
    if color==0:
        color_str='blanco'
    else:
        color_str='tinto'
    return('/static/images/vino_' +color_str+'_'+str(calidad)+'.jpg')




# antes del primer request
@app.before_first_request
def startup():
    global gbc
    gbc=pickle.load(open('data/gbc.p','rb'))
    global var
    var=pd.read_csv('data/vino_data.csv').drop('quality', axis=1).columns



# manejo de errores
@app.errorhandler(500)
def server_error(e):
    logging.exception('algun error...')
    return """
    And internal error <pre>{}</pre>
    """.format(e), 500



# conexion a traves de ruta
@app.route('/backend', methods=['POST', 'GET'])
def backend():
    # requests
    req=[request.args.get(e.replace(' ', '_')) for e in var]
    
    # nuevos datos
    n_data={k:v for k,v in zip(var, req)}
    n_data['color']=int(request.args.get('color'))
    
    X_pred=pd.DataFrame.from_dict(n_data, orient='index').T

    # prediccion
    prob=gbc.predict_proba(X_pred)

    pred=[3,6,9][np.argmax(prob[0])]
    
    return jsonify({'quality_prediction':pred, 
                    'image_name': imagen_vino(n_data['color'], pred)})


# principal
@app.route("/", methods=['POST', 'GET'])
def main():
    logging.warning('index!')
    # carga por defecto
    return render_template('index.html', 
                           quality_prediction=1, 
                           image_name='/static/images/vino_tinto_6.jpg')





# solo en local
if __name__=='__main__':
    app.run(debug=True)