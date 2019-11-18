// Index creation
CREATE INDEX ON :Item(itemId);
CREATE INDEX ON :Department(deptName);
CREATE INDEX ON :Category(catName);
CREATE INDEX ON :Brand(brandName);


// Import Clothing Materials Ontology
CALL semantics.importOntology("http://www.nsmntx.org/2019/10/clothingMaterials","Turtle", { keepLangTag: true, handleMultival: 'ARRAY'});


// Load data
LOAD CSV WITH HEADERS FROM "file:///next_products.csv"  AS row
MERGE (b:Brand { brandName : row.brandName })
MERGE (dep:Department { deptName: row.itemDepartmemnt })
MERGE (cat:Category { catName: row.itemCategory })
MERGE (i:Item { itemId: row.itemId }) ON CREATE set i.itemName = row.itemName, i.composition = row.itemComposition, i.url = row.url
MERGE (i)-[:IN_CAT]->(cat)
MERGE (i)-[:IN_DEPT]->(dep)
MERGE (i)-[:BY]->(b) ;

//Annotate your data with the ontology
MATCH (c:Class) UNWIND c.label as langLabel
WITH collect( {key: toLower(semantics.getValue(langLabel)), classNode: c }) as termToClassMap
MATCH (i:Item)
FOREACH (material IN [x in termToClassMap where toLower(i.composition) contains x.key | x.classNode ] | MERGE (i)-[:CONTAINS]->(material)) ;


//Extend the ontology with custom categories
:params onto: "@prefix owl: <http://www.w3.org/2002/07/owl#> . @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> . @prefix clmat: <http://www.nsmntx.org/2019/10/clothingMaterials#> . @prefix ccat: <http://www.nsmntx.org/customCats#> . <http://www.nsmntx.org/customCats>  a owl:Ontology ;  rdfs:comment 'Custom categories for semantic search system' ;  rdfs:label 'Custom categories' . ccat:AnimalBasedMaterial  a owl:Class ;  rdfs:label 'Animal-based material' . clmat:Leather rdfs:subClassOf ccat:AnimalBasedMaterial . clmat:Silk rdfs:subClassOf ccat:AnimalBasedMaterial . clmat:Wool rdfs:subClassOf ccat:AnimalBasedMaterial ."
CALL semantics.importOntologySnippet($onto,"Turtle", { keepLangTag: true, handleMultival: 'ARRAY'})


MATCH (:Category { catName: "Fleeces"})<-[:IN_CAT]-(i:Item)-[:BY]->(:Brand { brandName: "Columbia"})
RETURN i.itemId as id, i.itemName as name, i.url as url, i.composition as composition

MATCH (:Category { catName: "Hoodies"})<-[:IN_CAT]-(i:Item)-[:BY]->(b:Brand)
RETURN b.brandName as brand, count(i) as productCount ORDER BY productCount DESC LIMIT 5

MATCH (leather:Class { name: "Leather"})
CALL semantics.inference.nodesInCategory(leather, { inCatRel: "CONTAINS" }) yield node AS product
WITH product MATCH (product)-[:BY]->(b:Brand)
return product.itemName AS product, b.brandName AS brand, product.composition AS composition


MATCH (leather:Class { name: "Leather"})
CALL semantics.inference.nodesInCategory(leather, { inCatRel: "CONTAINS" }) yield node AS product
WITH product MATCH (product)-[:BY]->(b:Brand) AND NOT (product)-[:CONTAINS]->(leather)
return product.itemName AS product, b.brandName AS brand, product.composition AS composition


MATCH (item:Item) WHERE item.name CONTAINS $searchterm



