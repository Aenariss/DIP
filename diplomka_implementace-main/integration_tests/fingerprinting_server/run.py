#!/usr/bin/python
# -*- coding: UTF-8 -*-
from flask import Flask,render_template,Blueprint,request,jsonify
from flask import request                   # for reading url parameters
from fingerprint.attributes_manager import *
from flask_babel import Babel
from datetime import datetime
from functools import wraps

import env_config as config
import json
import hashlib
import os
import time
import re


###### App
app = Flask(__name__)
app.debug = config.debug

cwd = os.path.dirname(os.path.abspath(__file__))
attributes_folder = os.path.join(cwd, "fingerprint/attributes")

outputs_folder = os.path.join(cwd, "outputs")
generated_t = str(datetime.utcnow())
server_start = generated_t.replace(" ", "--").replace(":", "-").replace(".", "-")
start_pattern_month = r"\d{4}-\d{2}-\d{2}"
server_start_timestamp = re.search(start_pattern_month, server_start).group(0)

subfolder_path = os.path.join(outputs_folder, server_start_timestamp)
os.makedirs(subfolder_path, exist_ok=True)


attributes = Blueprint('site', __name__, static_url_path='', static_folder='fingerprint/attributes',url_prefix='')

tested_attr = config.tested_attributes

app.register_blueprint(attributes)
files,variables = get_files_and_variables(attributes_folder, tested_attr)
variablesWithHTTP = [["User-Agent"],["Accept"],["Accept-Language"],["Accept-Encoding"],["Connection"]]
variablesWithHTTP.extend(variables)
definitions = get_definitions(attributes_folder, tested_attr)
unspecifiedValue = "-"

_latest_timestamp = None
_subfolder = None

def change_latest_timestamp(ts):
    global _latest_timestamp
    _latest_timestamp = ts

def change_subfolder(sf):
    global _subfolder
    _subfolder = sf

def get_latest_timestamp():
    global _latest_timestamp
    return _latest_timestamp

def get_subfolder():
    global _subfolder
    return _subfolder


def get_locale():
    return 'en'

@app.route('/')
def home():
    print("home")
    time.sleep(5)
    exp = request.args.get('exp')
    browser = request.args.get('browser')
    pet = request.args.get('pet')
    params = [['_exp', exp], ['_browser', browser], ['_pet', pet]]
    time.sleep(5)
    return render_template('fp.html', files=files, variables=variables, headers=request.headers, params=params)

@app.route('/store', methods=['POST'])
def store():
    print("store")
    time.sleep(15)
    return json.dumps(out.storeFP(request, request.data,True))

###### Babel
babel = Babel(app)

babel.init_app(app, locale_selector=get_locale)
def get_locale():
    return request.accept_languages.best_match(config.LANGUAGES.keys())

###### DB
class Output(object):
    def storeFP(self, request, fingerprint,decode):
        try:
            
            generated_time = str(datetime.utcnow())
            outfile_time = generated_time.replace(" ", "--").replace(":", "-").replace(".", "-")

            if decode :
                parsedFP = json.loads(fingerprint.decode('utf-8'))
            else :
                parsedFP = fingerprint

            parsedFP = self.parse(request, parsedFP)
            parsedFP["generated_time"] = generated_time
            browserused = parsedFP["_browser"]
            addonsused = parsedFP["_pet"]

            start_pattern = r"\d{4}-\d{2}-\d{2}--\d{2}-\d{2}-\d{2}"
            
            start_timestamp = re.search(start_pattern, outfile_time).group(0)
            
            month_day_pattern = r"(\d{4}-\d{2}-\d{2})"
            month_day_folder = re.search(month_day_pattern, start_timestamp).group(0)

            if "None" in addonsused:
                change_latest_timestamp(start_timestamp)
                latest_timestamp = get_latest_timestamp()
                subfolder =  "outputs/" + month_day_folder + "/" + latest_timestamp + "_" + browserused
                change_subfolder(subfolder)
                output_dir = os.path.join(cwd, get_subfolder())
                os.makedirs(output_dir, exist_ok=True) 
            else:
                output_dir = os.path.join(cwd, get_subfolder())

            output_fn = os.path.join(output_dir, "log")
            output_fn = output_fn + "--" + outfile_time + "_" + browserused + "_" + addonsused + "_" + '.txt' 

            with open(output_fn, "w+") as out:
               json.dump(parsedFP, out, indent=4)
      
        except Exception as e:
            with open(output_fn, 'a+') as f:
                f.write(str(e))
    
    def parse(self, request, parsedFP):        
        #Adding adBlock information
        if "adBlock installed" not in parsedFP.keys():
            parsedFP["adBlock installed"] = "yes"
        
        #Convert certain attribute values into corresponding dictionaries
        dic = ["has user lied with", "screen", "storage", "touch support"] 
        for i in dic:
            if i not in parsedFP.keys():
                continue
            old = parsedFP[i]
            parsedFP[i] = self.convert_to(old, "dict")
        
        #Change the type of some attribute values into integers
        if "touch support" in parsedFP.keys():
            parsedFP["touch support"]["max touch points"] = int(parsedFP["touch support"]["max touch points"])

        if "screen" in parsedFP.keys():
            for key in parsedFP["screen"].keys():
                if parsedFP["screen"][key] != "undefined":
                    parsedFP["screen"][key] = int(parsedFP["screen"][key])

        # Hash canvas and webgl data if they are strings
        canvas_url_byte, canvas_data_byte, webgl_byte, canvas_blob_byte, webglURL_byte = None, None, None, None, None
        if "canvas" in parsedFP.keys() and "dataURL" in parsedFP["canvas"].keys():
            canvas_url_byte = bytes(str(parsedFP["canvas"]["dataURL"]), 'utf-8')

        if "canvas" in parsedFP.keys() and "imageData" in parsedFP["canvas"].keys():
            canvas_data_byte = bytes(str(parsedFP["canvas"]["imageData"]), 'utf-8')

        if "canvas_blob" in parsedFP.keys():
            canvas_blob_byte = bytes(str(parsedFP["canvas_blob"]), 'utf-8')

        if "WebGL" in parsedFP.keys() and "webGLpixels" in parsedFP["WebGL"].keys():
            webgl_byte = bytes(str(parsedFP["WebGL"]["webGLpixels"]), 'utf-8')

        if "WebGL" in parsedFP.keys() and "webGLdataURL" in parsedFP["WebGL"].keys():
            webglURL_byte = bytes(str(parsedFP["WebGL"]["webGLdataURL"]), 'utf-8')

            

        if canvas_url_byte is not None:
            canvas_URLhash = hashlib.sha1(canvas_url_byte)
            parsedFP["canvas"]["dataURL"] = canvas_URLhash.hexdigest()

        if canvas_data_byte is not None:
            canvas_Datahash = hashlib.sha1(canvas_data_byte)
            parsedFP["canvas"]["imageData"] = canvas_Datahash.hexdigest()

        if webgl_byte is not None:
            webgl_hash = hashlib.sha1(webgl_byte)
            parsedFP["WebGL"]["webGLpixels"] = webgl_hash.hexdigest()

        if webglURL_byte is not None:
            webglurl_hash = hashlib.sha1(webglURL_byte)
            parsedFP["WebGL"]["webGLdataURL"] = webglurl_hash.hexdigest()

        if canvas_blob_byte is not None:    
            canvas_blob_hash = hashlib.sha1(canvas_blob_byte)
            parsedFP["canvas_blob"] = canvas_blob_hash.hexdigest()

    
        return parsedFP

   
    def convert_to(self, old, type):
        if type == "dict":
            result = dict()
            old_lst = old.split(";")
            for i in old_lst:
                i = i.split(":")
                if (len(i) != 2):
                    continue
                key, val = i[0], i[1]
                result[key] = val
        elif type == "list":
            result = list()
            old_lst = old.split(";")
            for i in old_lst:
                if len(i) < 1:
                    continue
                result.append(i)

        return result
out = Output()


###### API
def jsonResponse(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return jsonify(func(*args, **kwargs))
    return wrapper

if __name__ == '__main__':
    app.run(threaded=True, ssl_context='adhoc')
