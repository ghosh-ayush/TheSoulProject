import csv
import ast
from neo4j import GraphDatabase

# Neo4j connection details (update as needed)
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "testpass"
ENRICHED_CSV = "enriched.csv"

# Helper to safely parse stringified lists/dicts

def safe_parse(val):
    try:
        return ast.literal_eval(val)
    except Exception:
        return val

def ingest():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
    with driver.session() as session, open(ENRICHED_CSV, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            # Node properties
            node_id = row.get('title')
            node_type = row.get('type', 'CONCEPT')
            node_props = {
                'id': node_id,
                'title': row.get('title'),
                'type': node_type,
                'summary': row.get('summary'),
                'aliases': safe_parse(row.get('aliases', '[]')),
                'tags': safe_parse(row.get('tags', '[]')),
            }
            # Create node
            if node_type:
                cypher = f"MERGE (n:Entity:{node_type} {{id: $id}}) SET n += $props"
            else:
                cypher = "MERGE (n:Entity {id: $id}) SET n += $props"
            session.run(
                cypher,
                id=node_id,
                props=node_props
            )
            # Create relationships
            relationships = safe_parse(row.get('relationships', '[]'))
            if isinstance(relationships, list):
                for rel in relationships:
                    if isinstance(rel, dict):
                        from_id = rel.get('from')
                        to_id = rel.get('to')
                        rel_type = rel.get('rel', 'RELATED_TO')
                        source = rel.get('source', '')
                        session.run(
                            "MERGE (a:Entity {id: $from_id}) MERGE (b:Entity {id: $to_id}) "
                            "MERGE (a)-[r:%s {source: $source}]->(b)" % rel_type,
                            from_id=from_id,
                            to_id=to_id,
                            source=source
                        )
    driver.close()

if __name__ == "__main__":
    ingest()
