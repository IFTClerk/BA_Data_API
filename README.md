# BA Data API

**Note: because how Werkzeug likes retrieving query parameters, a list of queries need to be passed as ``?foo=bar&foo=baz&foo=qux``**

# Available Endpoints
``/characters/phonebook``

Lists character names indexed by their IDs, query ``name_contains`` to find all entries that contain a substring

Query Parameters:
* ``name_contains=<name substring>``
* ``student_only=<[true]|false>``
* ``lang=<jp|kr|[en]|tw|th>``

---

``/characters/``

Prints out full unit details (basic info, stats, extra info, profile, skills, skill values, UE info, UE passive, bond stats). By default retrieves every single unit, including enemy units (VERY slow). Can be filtered with most fields available in basic info e.g. WeaponType, TacticRole, ...

Query Parameters:
* ``<Key>=<Value>``
  e.g. WeaponType=SR
* ``student_only=<[true]|false>``
* ``lang=<jp|kr|[en]|tw|th>``

---

``/characters/<ID>/``

``/characters/<ID>/<Info>``

Use the ``<ID>`` endpoint to specify a unit. Use the ``<Info>`` endpoint to view a specific table 

**Available ``<Info>`` values:**
```
'info': basic info for unit
'stats': unit base stats
'details': extra useless details, idk
'profile': unit profile
'skills': unit skill text
'skill_details': unit skill values, to my best ability
'weapon': UE info,
'weapon_passive': UE40 passive stat bonuses,
'bond': bonus stats from bond
```

Query Parameters:
* ``lang=<jp|kr|[en]|tw|th>``

---

``/assets/<Asset>/``

``/assets/<Asset>/<ID>``

Retrieves specific assets verbatim from data table, either all entries or by ID. Can filter by field values like characters

**Available ``<Asset>`` values:**
```
'skills': Skills (mostly useless)
'items': Items
'equipment': Equipment
'currencies': Currency
'furnitures': Furniture
'recipes': Recipes
```

Query Parameters:
* ``<Key>=<Value>``
  e.g. Rarity=N
* ``lang=<jp|kr|[en]|tw|th>``



# Installing and Running

1. Clone this repository
2. ``cd`` into the directory and run ``pip install .``
3. ``chmod +x run.sh; ./run.sh`` to start a simple WSGI development server
4. Visit localhost:5000 (by default) to interact with the application

Find your favourite deployment option on [Flask documentation](https://flask.palletsprojects.com/en/2.1.x/deploying/)

