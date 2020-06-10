from core.custom_function.utils.db_utils import *
from core.custom_function.utils.csv_utils import *
from core.custom_function.utils.inference_utils import *
import os
import time
import datetime
import shutil
import logging
def API_DB_CONNECT_TEST(db_connection_settings):
    d = DBOperation(db_connection_settings)
    if d:
        return 'ok'
    else :
        return d.error

def API_MONITOR_FOLDER(db_connection_settings,csv_settings,layer_settings):
    logging.info('----- start monitor folder ---------')
    error_logs =[]
    d = DBOperation(db_connection_settings)
    if d.status:
        #sum layer settings
        inference_ip = layer_settings['inference_ip']
        inference_port = layer_settings['inference_port']
        table_name = layer_settings['name']
        flag_rule = layer_settings['rules']
        csv_folder = csv_settings['csv_folder']
        processed_csv_folder = csv_settings['processed_csv_folder']
        os.makedirs(processed_csv_folder,exist_ok=True)
        measure_time_format = csv_settings['measure_time_format']
        predefined_db_csv_col = csv_settings['predefined_db_csv_col']
        #get csv list
        csv_list = get_csv_paths(csv_folder)
        msg='ok'
        #loop csv list
        for csv_file_path in csv_list:
            csv_name = os.path.split(csv_file_path)[-1]
            insert_data = []
            #parse csv data
            try:
                parsed_csv_index,parsed_csv_data = parsing_csv(csv_file_path)
                print(f'found data {len(parsed_csv_data)}')
                logging.info(f'found data {len(parsed_csv_data)}')
            except Exception as e:
                print(e)
                current_time = datetime.datetime.now()
                # msg = f'{current_time},{csv_name},'',inference error {str(e)}'
                msg = f"{current_time},{csv_name},inference error {str(e)}"
                logging.error(msg)
                error_logs.append(msg)
            #loop row thorugh csv data
            for row in parsed_csv_data:
                row_array = row.split(',')
                
                #csv data mapping use predefined csv col
                row_data = dict(zip(list(predefined_db_csv_col.keys()),row_array))
                #get file path
                img_path = row_data['FILENAME']
                try:
                    hashkey = row_data['HASH_KEY']
                except :
                    hashkey = row_data['HASHKEY']
                if os.path.exists(img_path):
                    #set update time
                    update_time = datetime.datetime.now()
                    row_data['UPDATE_TIME']=update_time

                    #convert measuere time format
                    row_data['MEASURE_TIME'] = convert_timestring(row_data['MEASURE_TIME'],measure_time_format)

                    #do inference
                    start_time = time.time()
                    code,result = do_inference(inference_ip,inference_port,[img_path])
                    if code==200:
                        row_data['CHECK_TIME'] = round((time.time()-start_time)*1000,2)
                        predicted = result['predicted'][0]
                        row_data['ITEM']=predicted
                        #set flag
                        if predicted in list(flag_rule.keys()):
                            row_data['FLAG'] = flag_rule[predicted]
                        else :
                            current_time = datetime.datetime.now()
                            msg = f'{current_time},{csv_name},{hashkey},rule key error {predicted}'
                            error_logs.append(msg)
                            row_data['FLAG']=-1
                        #insert into array
                        insert_data.append(row_data)
                    else :
                        current_time = datetime.datetime.now()
                        msg = f'{current_time},{csv_name},{hashkey},inference error {result}'
                        error_logs.append(msg)
                        logging.error(msg)
                        print(msg)
                else :
                    current_time = datetime.datetime.now()
                    msg = f'{current_time},{csv_name},{hashkey},image {img_path} not found error'
                    error_logs.append(msg)
                    logging.error(msg)
            DBO = DBOperation(db_connection_settings)
            if DBO.status:
                print('logging')
                column_names = layer_settings['columns']
                current_time = datetime.datetime.now()
                try:
                    # print('insertData',insert_data)
                    print('strat insert_data')
                    DBO.create(table_name,column_names,insert_data)
                    print('complete insert')
                    shutil.move(csv_file_path,os.path.join(processed_csv_folder,csv_name))
                except Exception as e:
                    print(e)
                    msg = f"{current_time},{csv_name},,db log error {DBO.error}"
                    print(msg)
                    logging.error(msg)
                    error_logs.append(msg)
            else :
                current_time = datetime.datetime.now()
                msg = f"{current_time},{csv_name},,db log connection error {DBO.error}"
                error_logs.append(msg)
                logging.error(msg)

    else :
        current_time = datetime.datetime.now()
        msg = f'{current_time},'','',db connection test error {d.error} '
        print(msg)
        error_logs.append(msg)
        logging.error(msg)

    return msg,error_logs

def API_INFERENCE_FLAG(l_settings,db_connection_settings):
    logging.info('----- start inference flag ---------')
    #get flag list
    error_logs = []
    query_condition = l_settings['query_condition']
    query_table_name = query_condition['table_name']
    condition = query_condition['condition']
    infernece_type = l_settings['type']
    table_name = l_settings['name']
    column_names = l_settings['columns']
    selected_columns = ['FILENAME','HASH_KEY']
    DBO = DBOperation(db_connection_settings)
    condition = l_settings['query_condition']['condition']
    process_list = DBO.read(query_table_name,selected_columns,condition)
    msg = 'ok'
    logging.info(f'found data from hashkey {len(process_list)}')
    if process_list!=None:
        for item in process_list:
            logging.info('start process flags')
            image_path = item[0]
            hashkey = item[1]
            inference_ip = l_settings['inference_ip']
            inference_port = l_settings['inference_port']
            code,result = do_inference(inference_ip,inference_port,[image_path])
            if code==200:
                if infernece_type=='detection':
                    offsets = l_settings['offsets']
                    insert_ds = detection_parsing_result(result,offsets,hashkey)
                    logging.info(f" found detection {len(insert_ds)} data ")

                    update_flag = l_settings['update_flag']
                    update_dict = {'FLAG':update_flag}
                    DBO = DBOperation(db_connection_settings)
                    if len(insert_ds)>0:                        
                        ##update original flag
                        print('start insert data')
                        logging.info(f"start insert data len {len(insert_ds)}")
                        DBO.create(table_name,column_names,insert_ds)
                        print('complete insert data')
                        logging.info(f"complete insert data")
                    
                    print('start update data')
                    logging.info(f"start update data")
                    DBO.update(query_table_name,update_dict,hashkey)
                    print('update finish')
                    logging.info(f"update finish")



                elif infernece_type=='classification' :
                    rules = l_settings['rules']
                    predicted = result['predicted'][0]
                    flag=-1
                    if predicted in list(rules.keys()):
                        flag = rules[predicted]                
                    update_dict = {'ITEM':predicted,'FLAG':flag}
                    DBO = DBOperation(db_connection_settings)
                    DBO.update(table_name,update_dict,hashkey)
                else :
                    msg = f'error type {infernece_type}'
                    print(msg)
                    logging.error(msg)
            else :
                current_time = datetime.datetime.now()
                msg = f'{current_time},{hashkey},inference error {result}'
                logging.error(msg)
                error_logs.append(msg)
                print(msg)
    return msg,error_logs