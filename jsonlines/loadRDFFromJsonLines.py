from zipfile import ZipFile
from neo4j import GraphDatabase

cypher_neosemantics = 'UNWIND  $payload as rdf_fragment  \
      CALL semantics.importRDFSnippet(rdf_fragment,"JSON-LD")  \
      YIELD terminationStatus, triplesLoaded, triplesParsed, extraInfo \
      RETURN terminationStatus, sum(triplesLoaded) as totalLoaded, sum(triplesParsed) as totalParsed '

jsonl_file_name = "lines.jsonl"

batch_size = 17

uri = "bolt://localhost:7687"


def load_batch(tx, batch):
    print("Submitting batch of size " + str(len(batch)))
    for record in tx.run(cypher_neosemantics, payload=batch):
        print('status: ', record["terminationStatus"], ', triplesLoaded: ', record["totalLoaded"],
              ', triplesParsed: ', record["totalParsed"])


driver = GraphDatabase.driver(uri, auth=("neo4j", "neo"))

with driver.session() as session:
    with ZipFile(jsonl_file_name + '.zip', 'r') as zip:
        with zip.open(jsonl_file_name, mode='r') as jsonl_file:
            batch = []
            for line in jsonl_file:
                batch.append(line.decode('utf-8'))
                if len(batch) == batch_size:
                    session.write_transaction(load_batch, batch)
                    batch = []
            session.read_transaction(load_batch, batch)

driver.close()


