import requests
import json
import rdflib

url = 'http://localhost:7474/rdf/cypher'

cypher = 'MATCH (nineties:Movie)-[rel]-(pers:Person) ' \
         'WHERE nineties.released >= 1998 AND nineties.released < 2000 ' \
         'RETURN nineties, rel, pers'

payload = { 'cypher' : cypher , 'format' : 'Turtle' }

response = requests.post(url, auth=('neo4j', 'neo'), data = json.dumps(payload))
response.raise_for_status()  # raise an error on unsuccessful status codes

g=rdflib.Graph()
g.parse(data=response.text, format='turtle')

for s,p,o in g:
    print (s,p,o)


