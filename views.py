from flask import Blueprint, render_template, request, redirect, url_for, flash, Flask, send_from_directory, jsonify
import random
import numpy as np
import os
from flask_socketio import SocketIO, emit, disconnect
import json

#from . import db
#from .models import Comment
#from flask_assets import Bundle, Environment
#import * as Tone from "tone"


global data
data = {}
data['connected'] = False
data['processed'] = False

class NumpyEncoder(json.JSONDecoder):
    def default(self, obj):
        if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
            np.int16, np.int32, np.int64, np.uint8,
            np.uint16, np.uint32, np.uint64)):
            return int(obj)
        elif isinstance(obj, (np.float_, np.float16, np.float32, 
            np.float64)):
            return float(obj)
        elif isinstance(obj,(np.ndarray,)): 
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

def jsonify(dic) :
    return json.loads(json.dumps(dic,cls=NumpyEncoder))

EEG_UPLOAD_FOLDER = os.path.join('uploads','sample')
ALLOWED_EXTENSIONS = {'npy'}

main = Flask(__name__)
main.config['EEG_UPLOAD_FOLDER'] = EEG_UPLOAD_FOLDER
main.secret_key = 'blabla'
socketio = SocketIO(main,pingInterval = 10000, pingTimeout= 5000)


@main.route('/')
def index():
    global data
    data['connected'] = False
    return render_template('index.html') #index.html 수정하기

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@main.route('/instruments')
def instruments():
    #data = np.load('/Users/hyeonah/Documents/dev/sonify/sample.npy')
    #print(data)
    return render_template('instruments.html')


@main.route('/upload', methods =['GET', 'POST'])
def upload_file():
    global data
    if request.method == 'POST' :
        if 'file' not in request.files : # sample <- file ???
            print('no file')
            flash('No file part')
            return redirect(request.url)
        file = request.files['file'] # sample -> file ???
        if file.filename == '':
            print('no file, empty')
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            print('upload successful, flle_name: ', file.filename)
            data['eeg_file_path'] = os.path.join(app.config['EEG_UPLOAD_FOLDER'], file.filename)
            file.save(data['eeg_file_path'])
            return render_template('select.html')
    return render_template('index.html')


@socketio.on('connect')
def connect():
    global data
    if not data['connected'] :
        data['connected'] = True

        data['signal_raw'] = np.load('/Users/hyeonah/Documents/dev/sonify/sample.npy').tolist()
        data['out'] = {
            'full_size':len(data['signal_raw'][0])}

        print('init =', data['out'])
        data['out'] = jsonify(data['out'])
        emit('connect', data['out'])


if __name__ == '__main__':
    socketio.run(main, debug=True)
    #app.run()