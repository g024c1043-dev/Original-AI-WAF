import json

def cleaned(data):
    if data is None:
        return None
    start = data.find("[")
    end = data.rfind("]")
    if start == -1 or end == -1:
         return None 
    else:
         json_part = data[start:end + 1]
    return json.loads(json_part)