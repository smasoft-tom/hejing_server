

import cx_Oracle
import json
import os
import datetime
import time
import shutil
import requests

def parsing_csv(csv_path,predefined_csv_col=None):
    col_dict = {
        "MEASURE_TIME":"MEASURE_TIME",
        "TOOLID":"TOOLID",
        "LOT":"LOT",
        "WAFER_NO":"WAFER_NO",
        "HASH_KEY":"HASHKEY",
        "FILENAME":"FILE"
        }
    if predefined_csv_col!=None:
        col_dict = predefined_csv_col
    with open(csv_path,'r',encoding='utf-8') as f:
        file_infos = f.read().splitlines()
        col_name = file_infos[0].replace('\ufeff','').split(',')
        file_infos = file_infos[1:]

    image_path_index = col_name.index(col_dict["FILENAME"])
    measure_time_index = col_name.index(col_dict["MEASURE_TIME"])
    toolid_index = col_name.index(col_dict['TOOLID'])
    wafer_no_index = col_name.index(col_dict['WAFER_NO'])
    hash_key_index = col_name.index(col_dict['HASH_KEY'])
    lot_index = col_name.index(col_dict['LOT'])
    cols_index = [measure_time_index,toolid_index,wafer_no_index,hash_key_index,image_path_index,lot_index]
    return cols_index ,file_infos

def get_csv_paths(csv_folder):
    csv_paths = []
    for i in os.scandir(csv_folder):
        if '.csv' in i.name:
            csv_paths.append(i.path)
    return csv_paths
def convert_timestring(measure_time,time_format):
    measure_time = measure_time.replace('-','/')
    measure_time_parse_string = time_format
    measure_time = datetime.datetime.strptime(measure_time, measure_time_parse_string)
    return measure_time
def convert_float_to_string(x):
    return str(round(x,2))