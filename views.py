from flask import Blueprint, render_template, request, redirect, url_for, flash, Flask, send_from_directory, jsonify
import random
import numpy as np
import os
from flask_socketio import SocketIO, emit, disconnect
import json

from scipy.signal import butter, lfilter
import mne
#import matplotlib.pyplot as plt
#import seaborn as sns

#from . import db
#from .models import Comment
#from flask_assets import Bundle, Environment
#import * as Tone from "tone"


global data
data = {}
data['connected'] = False
data['processed'] = False
cond='p10'
tmin=-0.05
tmax=0.17

class NumpyEncoder(json.JSONEncoder):
    """ JSON Encoder for Numpy ndarrays """
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
        return json.JSONEncoder.defasult(self, obj)

def jsonify(dic) :
    return json.loads(json.dumps(dic,cls=NumpyEncoder))

EEG_UPLOAD_FOLDER = os.path.join('uploads','sample')
ALLOWED_EXTENSIONS = {'npy'}

main = Flask(__name__)
main.config['EEG_UPLOAD_FOLDER'] = EEG_UPLOAD_FOLDER
main.secret_key = 'blabla'
socketio = SocketIO(main, pingInterval = 10000, pingTimeout= 50000)

def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

def run():
    import numpy as np
    import pywt
    from scipy.signal import freqz
    from scipy.signal import find_peaks_cwt
    from numpy import save

    sample = np.load('/Users/hyeonah/Documents/dev/sonify/sample.npy')
    fre_data = sample[0]
    # Sample rate and desired cutoff frequencies (in Hz).
    fs = 200.0 # 200
    lowcut = 10.0  
    highcut = 90.0

    # Get real amplitudes of FFT (only in positive frequencies)
    #fft_vals = np.absolute(np.fft.rfft(data))
    
    # Get positive data
    #data_y = np.absolute(data)
    
    # Get frequencies for amplitudes in Hz
    #fft_freq = np.fft.rfftfreq(len(data), 1.0/fs)
    
    # Plot the frequency response for a few different orders.
    for order in [3, 6, 9]:
        b, a = butter_bandpass(lowcut, highcut, fs, order=order)
        w, h = freqz(b, a, worN=2000)
        #plt.plot((fs * 0.5 / np.pi) * w, abs(h), label="order = %d" % order)

    # Filter a noisy signal.
    T = 0.05
    nsamples = T * fs
    t = np.arange(fre_data.size) / fs
    x = fre_data
    y = butter_bandpass_filter(x, lowcut, highcut, fs, order=5)
    
    band_eeg = np.r_[[t],[y]]
    
    coeffs = pywt.wavedec(y, 'db4', level=6)
    cA2, cD1, cD2,cD3,cD4,cD5,cD6 = coeffs

    cD1peaks = find_peaks_cwt(cD1, np.arange(1,5))
    cD2peaks = find_peaks_cwt(cD2, np.arange(1,5))
    cD3peaks = find_peaks_cwt(cD3, np.arange(1,5))
    cD4peaks = find_peaks_cwt(cD4, np.arange(1,5))
    cD5peaks = find_peaks_cwt(cD5, np.arange(1,5))
    cD6peaks = find_peaks_cwt(cD6, np.arange(1,5))
    
    cD1peaks = [x for x in cD1peaks if cD1[x]> 0]
    cD2peaks = [x for x in cD2peaks if cD2[x]> 0]
    cD3peaks = [x for x in cD3peaks if cD3[x]> 0]
    cD4peaks = [x for x in cD4peaks if cD4[x]> 0]
    cD5peaks = [x for x in cD5peaks if cD5[x]> 0]
    cD6peaks = [x for x in cD6peaks if cD6[x]> 0]

    #print(cD2[cD2peaks])
    #print(cD1peaks)
    #print(cD1)
    #print(len(cD1))
    
    arrDelta = np.zeros(2000)
    arrTheta = np.zeros(2000)
    arrAlpha = np.zeros(2000)
    arrBeta = np.zeros(2000)
    arrGamma = np.zeros(2000)
    #print(arrD1)
    print(cD1peaks)
    
    for idx in range(len(arrDelta)):
        if idx in cD1peaks:
            val = int(cD1[idx]*100)
            arrDelta[idx] = val
            
    for idx in range(len(arrTheta)):
        if idx in cD2peaks:
            val = int(cD2[idx]*100)
            arrTheta[idx] = val
            #print(val)
            
    for idx in range(len(arrAlpha)):
        if idx in cD3peaks:
            val = int(cD3[idx]*100)
            arrAlpha[idx] = val
            #print(val)
            
    for idx in range(len(arrBeta)):
        if idx in cD4peaks:
            val = int(cD4[idx]*100)
            arrBeta[idx] = val
            #print(val)
    
    for idx in range(len(arrGamma)):
        if idx in cD5peaks:
            val = int(cD5[idx]*100)
            arrGamma[idx] = val
            #print(val)
    
    #save('theta.npy',arrTheta)
    
    freq_arr = np.vstack([arrAlpha, arrBeta, arrGamma, arrDelta, arrTheta])
    #print(freq_arr)
    save('eeg_freq.npy',freq_arr)

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

"""
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
            data['eeg_file_path'] = os.path.join(app.confi
            g['EEG_UPLOAD_FOLDER'], file.filename)
            file.save(data['eeg_file_path'])
            return render_template('select.html')
    return render_template('index.html')
"""

@socketio.on('connect')
def connect():
    global data
    if not data['connected'] :
        data['connected'] = True

        socketio.sleep(0)
        #npdata = np.load('/Users/hyeonah/Documents/dev/sonify/sample.npy')[:,:200]
        run()
        npdata = np.load('/Users/hyeonah/Documents/dev/sonify/eeg_freq.npy')[:,:200]
        #print(npdata.shape)
        data['signal_raw'] = npdata.tolist()
        data['out'] = {
            'raw' : data['signal_raw'],\
            'full_size':len(data['signal_raw'][0])
            #'full_size':len(data['signal_raw'])
            }

        #print('init =', data['out'])
        data['out'] = jsonify(data['out'])
        emit('connect', data['out'])

if __name__ == '__main__':
    socketio.run(main, debug=True)
    #cabr_individual(0.05,0.17)
    #app.run()