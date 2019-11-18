from extruct.rdfa import RDFaExtractor
import requests
import json
from neo4j import GraphDatabase
import feedparser


def get_rss(url):
    feed = feedparser.parse(url)['entries'] or []
    feed_as_jsonld = [{'@context': 'http://schema.org', '@id': entry.get('id'), '@type': 'Article',
                       'datePublished': entry.get('published'), 'headline': entry.get('title'),
                       'about': [{'@type': 'Category', 'name': tag.term, '@id': tag.scheme} for tag in entry.tags],
                       'abstract': entry.get('summary')} for entry in feed]
    return json.dumps(feed_as_jsonld), [entry.get('id') for entry in feed]


def get_article_additional_details(url):
    print('Retrieving page ' + url)
    r = requests.get(url)
    data = rdfa_ext.extract(r.text, base_url=url)
    subset = [x for x in data if x['@id'] == url]
    authorlist = subset[0].get('article:author') or []
    authors = authorlist[0] if len(authorlist) > 0 else {}
    authors = [{'@id': a, '@type': 'Person'}
               for a in (authors.get('@value') or '').split(',')
               if a.startswith('http')]
    sections = [{'@id': 'guardian:' + s['@value'], '@type': 'Section'} for s in subset[0].get('article:section') or []]
    json_ld_as_map = {'@context': 'http://schema.org', '@id': url, 'author': authors, 'section': sections}
    return json.dumps(json_ld_as_map)


def load_json_ld(tx, json_ld_data):
    cypher_neosemantics = " CALL semantics.importRDFSnippet($payload,'JSON-LD');"
    import_summary = tx.run(cypher_neosemantics, payload=json_ld_data)
    print(import_summary)


uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "neo"))

rss_entries_as_json_ld, entry_url_list = get_rss('https://www.theguardian.com/uk/rss')

with driver.session() as session:
    session.write_transaction(load_json_ld, rss_entries_as_json_ld)
    rdfa_ext = RDFaExtractor()
    for url in entry_url_list:
        session.write_transaction(load_json_ld, get_article_additional_details(url))

driver.close()
