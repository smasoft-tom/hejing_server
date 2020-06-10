import sys,os
import logging
import time
from flask import request, Flask,Response
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
import json
import shutil
import requests
import traceback
from core.custom_function.API import apis
import subprocess
app = Flask(__name__)
def init(log_path):
    def read_json(p):
        with open(p,'r') as f:
            return json.loads(f.read())
    global db_connection_settings,csv_settings,layer_settings
    db_connection_settings = read_json('./init/custom/db_connection_settings.json')
    layer_settings = read_json('./init/custom/layer_settings.json')
    csv_settings = read_json('./init/custom/csv_settings.json')

    if os.path.exists('./central_server.exe'):
        process = subprocess.Popen(['./central_server.exe'])
    else :
        print('failed to launch central_server.exe')


    #logging errors
    logging.basicConfig(level=logging.DEBUG, filename=log_path)


#db_connection_test
@app.route("/db_connection_test", methods=['POST'])
def db_connection_test():
    try:
        result = apis.API_DB_CONNECT_TEST(db_connection_settings)
    except Exception as e:
        error_class = e.__class__.__name__ #取得錯誤類型
        detail = e.args[0] #取得詳細內容
        cl, exc, tb = sys.exc_info() #取得Call Stack
        lastCallStack = traceback.extract_tb(tb)[-1] #取得Call Stack的最後一筆資料
        fileName = lastCallStack[0] #取得發生的檔案名稱
        lineNum = lastCallStack[1] #取得發生的行號
        funcName = lastCallStack[2] #取得發生的函數名稱
        result = "File \"{}\", line {}, in {}: [{}] {}".format(fileName, lineNum, funcName, error_class, detail)
    reply = {'result':result}
    logging.error(result)
    return Response(json.dumps(reply),mimetype='application/json')
#scan files for layer 1
@app.route('/monitor_folder',methods=['POST'])
def monitor_folder():
    # sum_layer = layer_settings['sum_layer']
    request_json = request.json
    if request_json==None:
        request_json = r'{}'.format(request.stream.read().decode('utf-8'))
        request_json = json.loads(request_json)
    layer_name = request_json['layer_name']
    sum_layer = layer_settings[layer_name]
    print(sum_layer)
    try:
        print(csv_settings)
        csv_settings['csv_folder'] = sum_layer['csv_path']
        csv_settings['processed_csv_folder'] = os.path.join(sum_layer['csv_path'],'processed_csv')
        print(csv_settings)
    except Exception as e:
        print(e)
    try:
        result,error_msg = apis.API_MONITOR_FOLDER(db_connection_settings,csv_settings,sum_layer)
    except Exception as e:
        print(e)
        error_class = e.__class__.__name__ #取得錯誤類型
        detail = e.args[0] #取得詳細內容
        cl, exc, tb = sys.exc_info() #取得Call Stack
        lastCallStack = traceback.extract_tb(tb)[-1] #取得Call Stack的最後一筆資料
        fileName = lastCallStack[0] #取得發生的檔案名稱
        lineNum = lastCallStack[1] #取得發生的行號
        funcName = lastCallStack[2] #取得發生的函數名稱
        result = "File \"{}\", line {}, in {}: [{}] {}".format(fileName, lineNum, funcName, error_class, detail)
        logging.error(result)
        print(result)
    reply = {'result':result}
    
    return Response(json.dumps(reply),mimetype='application/json')

@app.route('/inference_flag',methods=['POST'])
def inference_flag():
    request_json = request.json
    if request_json==None:
        request_json = r'{}'.format(request.stream.read().decode('utf-8'))
        request_json = json.loads(request_json)
    layer_name = request_json['layer_name']
    l_settings = layer_settings[layer_name]
    try:
        result,error_msg = apis.API_INFERENCE_FLAG(l_settings,db_connection_settings)
    except Exception as e:
        error_class = e.__class__.__name__ #取得錯誤類型
        detail = e.args[0] #取得詳細內容
        cl, exc, tb = sys.exc_info() #取得Call Stack
        lastCallStack = traceback.extract_tb(tb)[-1] #取得Call Stack的最後一筆資料
        fileName = lastCallStack[0] #取得發生的檔案名稱
        lineNum = lastCallStack[1] #取得發生的行號
        funcName = lastCallStack[2] #取得發生的函數名稱
        result = "File \"{}\", line {}, in {}: [{}] {}".format(fileName, lineNum, funcName, error_class, detail)
        print(result)
        logging.error(result)
    reply = {'result':result}
    return Response(json.dumps(reply),mimetype='application/json')

if __name__ == "__main__":
    #check reg
    exe_log_path='./log/custom_server.log'
    os.makedirs(os.path.split(exe_log_path)[0],exist_ok=True)
    init(exe_log_path)

    #open server
    port = int(os.environ.get('PORT',7991))
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(port, address="0.0.0.0")
    #start server
    print('server started')
    try:
        IOLoop.instance().start()
    except KeyboardInterrupt:

        IOLoop.instance().stop()