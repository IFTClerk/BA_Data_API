import re

_re_isint = re.compile(r'^[-+]?\d+$')
_re_isfloat = re.compile(r'^[-+]?\d*\.\d+$')

def to_possible_types(value):
    if re.search(_re_isint, value):
        return int(value)
    elif re.search(_re_isfloat, value):
        return float(value)
    elif value.lower() in ['true', 'false']:
        return value.lower()=='true'
    
    return value
    