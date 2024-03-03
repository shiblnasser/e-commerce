import base64
import json

def decode(request_json):
    try:
        if request_json.get("data", ""):
            request_json = json.dumps(request_json.get("data", ""))
            
            base64_bytes = request_json.encode("ascii") 
            base64_bytes = base64.b64decode(base64_bytes) 
            base64_string = base64_bytes.decode("ascii") 
            return base64_string 
        
        else:
            return request_json    
    except:
        return {}
    
def validate_json(request_json, validation_json):
   
    status = True
    for key,data_type in validation_json.get("required", {}).items():
        if key not in request_json or type(request_json.get(key))!= data_type:
            status = False
            break
    if status:
        for key,data_type in validation_json.get("optional", {}).items():
            if key in request_json and type(request_json.get(key))!= data_type:
                status = False
                break
    return status
    


def format_json(request_json):
    final_json = {}
    for key, value in request_json.items():
        final_json[key] = value[0]
    return final_json


def encode(request_json):

    request_json = json.dumps(request_json)
    request_json_bytes = request_json.encode("ascii") 
    base64_bytes = base64.b64encode(request_json_bytes) 
    base64_string = base64_bytes.decode("ascii") 
    return base64_string



def get_username(session):

    if session:
        return session.get("username")
    
MESSAGES = {"DEFAULT":"Error ocurred", "INVALID_DATA_TYPE":"Please enter valid datatype"}


def get_all_dirs(data):
   
    final_json = {}
    for key in dir(data):
        final_json[key] = getattr(data,key)

    return final_json