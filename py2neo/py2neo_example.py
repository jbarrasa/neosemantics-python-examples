from py2neo import Graph


g = Graph("bolt://localhost:7687", user="neo4j", password="neo")
cypher = "CALL semantics.importRDF('https://raw.githubusercontent.com/jbarrasa/neosemantics/3.5/docs/rdf/nsmntx.ttl','Turtle', { handleVocabUris: 'IGNORE' })"
result = g.run(cypher).data()
print(result)