import json

def Message_serialization(message):
    return json.dumps(message).encode('utf-8')       #序列化

def Message_deserialization(message):
    return json.loads(message.decode('utf-8'))        #反序列化