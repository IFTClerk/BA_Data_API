from flask import Flask, request
from badapi.reader import BAData, BACharacter
from badapi.localization import Localization
from badapi.encoder import NumpyEncoder
from badapi.helper import to_possible_types

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.json_encoder = NumpyEncoder

bad = BAData()

@app.route('/')
def index():
    return 'You are on the index page. Shoo.'

@app.route('/characters/phonebook')
def list_characters():
    
    stonly = request.args.get("student_only", default=True, type=lambda v: v.lower() == 'true')
    contains = request.args.get('name_contains', '')
    lang = request.args.getlist('lang')
    
    return bad.list_characters(substr=contains, student_only=stonly, lang=Localization(*lang))

#### IMPLEMENT FILTER BY LOOKUP KEYS USING QUERY PARAMETERS
### for both characters and other resources
@app.route('/characters/')
@app.route('/characters/<int:idee>/')
@app.route('/characters/<int:idee>/<string:resource>')
def fetch_characters(idee=None, resource=None):
    
    stonly = request.args.get("student_only", default=True, type=lambda v: v.lower() == 'true')
    lang = Localization(*request.args.getlist('lang'))
    
    # get lookup keys
    lkey = []
    lvalue = []
    
    if idee is None:
        pass
    else:
        lkey.append('CharacterId')
        lvalue.append([idee])
        
    for arg, val in request.args.lists():
        if arg=='lang':
            continue
        lkey.append(arg)
        lvalue.append(list(map(to_possible_types, val)))
        
    # find characters based on lookup keys
    characters = bad.find_character(lkey, lvalue, student_only=stonly)
    data = {}
    for c_id in characters:
        character = BACharacter(bad, c_id, lang=lang)

        resource_funcs = {
            'info': character.basic_info,
            'stats': character.stats,
            'details': character.details,
            'profile': character.profile,
            'skills': character.skills,
            'skill_details': character.skill_details,
            'weapon': character.weapon,
            'weapon_passive': character.weapon_passive,
            'bond': character.bond
        }
    
        if resource is None:
            data[c_id] = character.summary()
        elif resource in resource_funcs.keys():
            data[c_id] = (resource_funcs[resource])()
        else:
            continue
            
    return data
    
@app.route('/assets/<string:resource>/')
@app.route('/assets/<string:resource>/<int:idee>')
def fetch_resource(resource=None, idee=None):
    
    lang = Localization(*request.args.getlist('lang'))
    
    resource_funcs = {
        'skills': bad.get_skill,
        'items': bad.get_item,
        'equipment': bad.get_equipment,
        'currencies': bad.get_currency,
        'furnitures': bad.get_furniture,
        'recipes': bad.get_recipe
    }
    
    lkey = []
    lvalue = []
    
    if idee is None:
        pass
    else:
        lkey.append('Id')
        lvalue.append([idee])
        
    for arg, val in request.args.lists():
        if arg=='lang':
            continue
        lkey.append(arg)
        lvalue.append(list(map(to_possible_types, val)))
        
    return (resource_funcs[resource])(lookup_key=lkey, lookup_value=lvalue, lang=lang)
