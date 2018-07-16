#!/usr/bin/env python

from flask import Flask
from flask import make_response
from flask import render_template
from flask import request
from flask_httpauth import HTTPBasicAuth
import hashlib
import json
import os

app = Flask(__name__)
auth = HTTPBasicAuth()

# Setting containing Username/ Pass and Allowed IP address
# This can be further modularized by placing the file outside of the Main
my_settings = {
    "upload_path": "./uploads",
    "users": {
        "john": "hello",
        "susan": "bye"
    },
    "allowed_ips": ['127.0.0.1','172.20.0.1']
}


# Basic Username & Password checking by pairing
@auth.get_password
def get_pw(username):
    if username in my_settings['users']:
        return my_settings['users'].get(username)
    return None


# Using api URI path to 
@app.route("/api/v1/files/<filename>", methods=['GET', 'POST', 'DELETE'])
@auth.login_required
def route_files(filename):
    if request.remote_addr not in my_settings['allowed_ips']:
        return "", 403
    if request.method == 'POST':
        f = request.files['file']
        f.save(my_settings['upload_path'] + "/" + filename)
        resp = make_response('{"result" : "true"}', 201)
        resp.headers['Content-Type'] = 'application/json'
        merge_if_file_similar("/" + f.filename)
        return resp
    elif request.method == 'DELETE':
        try:
            os.remove(my_settings['upload_path'] + "/" + filename)
            resp = make_response('{"result" : "true"}', 202)
            resp.headers['Content-Type'] = 'application/json'
            return resp
        except FileNotFoundError:
            resp = make_response('{"result" : "false"}', 404)
            resp.headers['Content-Type'] = 'application/json'
            return resp
    else:
        try:
            file_object  = open(my_settings['upload_path'] + "/" + filename, "rb")
            data = file_object.read()
            resp = make_response(data, 200)
            resp.headers['Content-disposition'] = "attachment; filename=%s" % filename
            resp.headers['Content-Type'] = 'application/octet-stream'
            return resp
        except FileNotFoundError:
            return "", 404
    
@app.route("/api/v1/files/", methods=['GET', 'POST'])
@auth.login_required
def route_files_root():
    if request.method == 'POST':
        files = request.files.getlist('files[]')
        print(files)
        
        for f in files:
            f.save(my_settings['upload_path'] + "/" + f.filename)
            merge_if_file_similar("/" + f.filename)
        resp = make_response('{"result" : "true"}', 201)
        resp.headers['Content-Type'] = 'application/json'
        return resp
    else:
        if request.remote_addr not in my_settings['allowed_ips']:
            return "",403
        resp = make_response(json.dumps(get_files()), 200)
        resp.headers['Content-Type'] = 'application/json'
        return resp

@app.route("/", methods=['GET'])
def route_root():
    return render_template("index.html", files=get_files())
    
def get_files():
    ret_files = []
    for path, dirs, files in os.walk(my_settings['upload_path']):
        for filename in files:
            ret_files.append((os.path.join(path, filename)).replace(my_settings['upload_path'], ""))
    return ret_files

def merge_if_file_similar(filename1):
    hashes = {}
    for filename in get_files():
        if(filename == filename1):
            continue
        file_object  = open(my_settings['upload_path'] + filename, "rb")
        data = file_object.read()
        #setattr(hashes, hashlib.md5(data).hexdigest(), filename)
        hashes[hashlib.md5(data).hexdigest()] = filename
        print(my_settings['upload_path'] + filename)
    print(hashes)
    file_object  = open(my_settings['upload_path'] + filename1, "rb")
    data = file_object.read()
    data_md5 = hashlib.md5(data).hexdigest()
    print(data_md5)
    try:
        if(hashes[data_md5] != ''):
            print("merging file" + filename1 + " with " + hashes[hashlib.md5(data).hexdigest()])
            os.remove(my_settings['upload_path'] + "/" + filename1)
            print(my_settings['upload_path'] + hashes[hashlib.md5(data).hexdigest()], my_settings['upload_path'] + filename1)
            os.link(my_settings['upload_path'] + hashes[hashlib.md5(data).hexdigest()], my_settings['upload_path'] + filename1)
    except:
        print("Here")
        return False


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
