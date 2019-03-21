import json
from json import JSONDecoder
from json import JSONEncoder
import datetime

class DateTimeDecoder(json.JSONDecoder):

    def __init__(self, *args, **kargs):
        JSONDecoder.__init__(self, object_hook=self.dict_to_object,
                             *args, **kargs)
    
    def dict_to_object(self, d): 
        if '__type__' not in d:
            return d

        type = d.pop('__type__')
        try:
            dateobj = datetime.datetime(**d)
            return dateobj
        except:
            d['__type__'] = type
            return d
            
class DateTimeEncoder(JSONEncoder):
    """ Instead of letting the default encoder convert datetime to string,
        convert datetime objects into a dict, which can be decoded by the
        DateTimeDecoder
    """
        
    def default(self, obj):
        if isinstance(obj, datetime.time):
            return {
                '__type__' : 'datetime.time',
                'hour' : obj.hour,
                'minute' : obj.minute,
                'second' : obj.second,
            }   
        else:
            return JSONEncoder.default(self, obj)




