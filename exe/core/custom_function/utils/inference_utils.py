import requests
from core.custom_function.utils.csv_utils import *

def do_inference(inference_ip,inference_port,image_paths):
    url = f"http://{inference_ip}:{inference_port}/smaseq/upload"
    files = []
    for img_path in image_paths:
        files.append(('file',open(img_path,'rb')))
    re = requests.post(url,files=files)
    code = re.status_code
    if code==200:
        return code,re.json()['result']
    else :
        return code,re.text


def detection_parsing_result(result,offsets,hashkey):
    offset_x = offsets['x']
    offset_y = offsets['y']
    insert_ds = []
    if len(result['predicted'])>0:
        predicted = result['predicted'][0]
        boxes = result['boxes'][0]
        defect_no = len(predicted)
        for idx,(class_name,box) in enumerate(zip(predicted,boxes)):
            width = convert_float_to_string(float(box[3])-float(box[1]))
            height = convert_float_to_string(float(box[2])-float(box[0]))
            defect_size = convert_float_to_string(float(width)*float(height))
            site_x = convert_float_to_string((float(box[3])+float(box[1]))/2-offset_x)
            site_y = convert_float_to_string((float(box[2])+float(box[0]))/2-offset_y)
            insert_d = {
                'HASH_KEY':hashkey,
                'DEFECT_NO':str(idx+1),
                'SITE_X':site_x,
                'SITE_Y':site_y,
                'DEFECT_SIZE':defect_size,
                'ITEM2':class_name
            }
            print(insert_d)
            insert_ds.append(insert_d)

    return insert_ds