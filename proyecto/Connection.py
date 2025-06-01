from neo4j import GraphDatabase

class Neo4jConnection:
    def __init__(self, uri, user, pwd, db="neo4j"):
        try:
            # Para Neo4j Aura (URI con neo4j+s://) NO configurar encrypted manualmente
            self.driver = GraphDatabase.driver(
                uri, 
                auth=(user, pwd)
                # NO incluir encrypted=True ni trust= para Aura
            )
            self.database = db
            print(f"✅ Conexión exitosa a {uri}")
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            raise

    def close(self):
        if self.driver:
            self.driver.close()

    def run_query(self, query, parameters=None):
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(query, parameters or {})
                return list(result)
        except Exception as e:
            print(f"Error ejecutando consulta: {e}")
            raise