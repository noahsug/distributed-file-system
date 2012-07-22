##
# Handles serialization and deserialization.
##

import pickle

def serialize(obj):
    return pickle.dumps(obj)

def deserialize(str):
    obj = None
    try:
        obj = pickle.loads(str)
    except Exception, ex:
        pass
    return obj
