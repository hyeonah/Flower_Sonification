import os
from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory
from flask_socketio import SocketIO, emit, disconnect

import json
import numpy as np


global data
data = {}
data['connected'] = False
data['processed'] = False
data['media_file_paths'] = [] # ?? 이건 빼줘도 될 듯

class NumpyEncoder(json.JSONDecoder):
    def default(self, obj):
        if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
            np.int16, np.int32, np.int64, np.uint8,
            np.uint16, np.uint32, np.uint64)):
            return int(obj)
        elif isinstance(obj, (np.float_, np.float16, np.float32, 
            np.float64)):
            return float(obj)
        elif isinstance(obj,(np.ndarray,)): #### This is the fix
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

def jsonify(dic) :
    return json.loads(json.dumps(dic,cls=NumpyEncoder))

EEG_UPLOAD_FOLDER = os.path.join('uploads','sample')
ALLOWED_EXTENSIONS = {'npy'}

app = Flask(__name__)
app.config['EEG_UPLOAD_FOLDER'] = EEG_UPLOAD_FOLDER
app.secret_key = 'blabla'
socketio = SocketIO(app.pingInterval = 10000, pingTimeout = 5000)  # 이건 뭐지


@main.route('/')
def index():
    global data
    data['connected'] = False
    return render_template('index.html') #index.html 수정하기

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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

@main.route('/instruments')
def instruments():
    data = np.load('/Users/hyeonah/Documents/dev/sonify/sample.npy')
    print(data)

@socketio.on('connect')
def connect():
    global data
    if not data['conntected'] :
        #emit('edf_info', load_edf())
        data['connected'] = True

@socketio.on('init_process')
def raw_process(dic) :
    global data
    emit('process_message', 'Filtering Data...')
    socketio.sleep(0)

    print('processing raw data ...')

    data['signal_raw'] = np.load('/Users/hyeonah/Documents/dev/sonify/sample.npy').list()
    data['out'] = jsonify(data['out'])
    emit('init_data', data['out'])

    print('init batch sent, num_samples=', len(data['out']['raw']))

if __name__ == '__main__':
    socketio.run(app, debug=True)
    #app.run()