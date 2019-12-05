from neo4j import GraphDatabase

def import_countries(tx):
    sparql_countries_query = """
    PREFIX sch: <http://schema.org/>
    CONSTRUCT { 
        ?ctry a sch:Country; 
              sch:identifier ?ctryISOCode ;
              sch:name ?countryName ;
              wdt:sharesBorderWith ?otherCountry }
    WHERE {
        ?ctry wdt:P31 wd:Q3624078 ; rdfs:label ?countryName .
        filter (lang(?countryName) = "en")
        optional { ?ctry wdt:P297 ?ctryISOCode }
        optional { ?ctry wdt:P47 ?otherCountry .
                   ?otherCountry wdt:P31 wd:Q3624078 }
    }"""

    print('Importing countries...')
    cypher_countries_query = """CALL semantics.importRDF(
    "https://query.wikidata.org/sparql?query=" + apoc.text.urlencode($sparql), "JSON-LD", 
    { headerParams: { Accept: "application/ld+json"} , handleVocabUris: "IGNORE"})"""

    for record in tx.run(cypher_countries_query, sparql=sparql_countries_query):
        print('importResult: ', record["terminationStatus"], ', triplesLoaded: ', record["triplesLoaded"])


def import_continents(tx, country_uri ):
    sparql_continents_query = " " \
    "PREFIX sch: <http://schema.org/> " \
    "CONSTRUCT { ?continent a sch:Continent ; " \
    "              sch:containsPlace ?ctry ; " \
    "               rdfs:label ?continentName  } " \
    "WHERE { " \
    "  ?ctry wdt:P30 ?continent . " \
    "  filter(?ctry = <" + country_uri + ">) " \
    "  ?continent rdfs:label ?continentName . " \
    "  filter (lang(?continentName) = 'en')    " \
    "} "

    print('Importing extra info for ', country_uri)
    cypher_countries_query = """CALL semantics.importRDF(
    "https://query.wikidata.org/sparql?query=" + apoc.text.urlencode($sparql), "JSON-LD", 
    { headerParams: { Accept: "application/ld+json"} , handleVocabUris: "IGNORE"})"""



    for record in tx.run(cypher_countries_query, sparql=sparql_continents_query):
        print('importResult: ', record["terminationStatus"], ', triplesLoaded: ', record["triplesLoaded"])


uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "neo"))

with driver.session() as session:
    #load countries
    session.write_transaction(import_countries)
    #load extra info for Spain (Q29)
    session.write_transaction(import_continents, 'http://www.wikidata.org/entity/Q29')
    #load extra info for Kazakhstan (Q232)
    session.write_transaction(import_continents, 'http://www.wikidata.org/entity/Q232')
    #...

driver.close()
