encode = None
decode = None
mode = None

"""
try:
 import cjson
 def encode(val):
   val = cjson.encode(val)
   #return val.replace('\\', '')
   return val
 #encode = cjson.encode
 decode = cjson.decode
 mode = 'cjson'
except:
 try:
  import json
  #encode = json.JSONEncoder().encode
  #decode = json.JSONDecoder().decode
  encode = json.dumps
  decode = json.loads
  mode = 'json'
 except:
  import simplejson
  encode = simplejson.dumps
  decode = simplejson.loads
  mode = 'simplejson'
"""

import json
encode = json.dumps
decode = json.loads
