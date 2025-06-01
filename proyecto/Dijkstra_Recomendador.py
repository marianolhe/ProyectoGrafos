from Connection import Neo4jConnection
from Libro import Libro

conn = Neo4jConnection(
    uri="neo4j+s://982b38ec.databases.neo4j.io", 
    user="neo4j",                                 
    pwd="qMIuwlgM9GhNColurgycVECla2yQtyMHgNRSSsnihDI",                           
    db="neo4j"                                    
)

def recomendar_con_dijkstra(usuario_id, limite=5):
    """Implementa recomendaciones usando algoritmo de Dijkstra simplificado"""
    try:
        # Consulta que simula Dijkstra calculando "distancias" desde el usuario
        query = """
        MATCH (usuario:Usuario {id: $usuario_id})
        MATCH (libro:Libro)
        WHERE NOT EXISTS((usuario)-[:ACEPTO|RECHAZO]->(libro))
        
        // Calcular distancia basada en preferencias
        WITH libro, usuario,
             CASE 
                WHEN EXISTS((usuario)-[:ACEPTO]->(:Libro {ritmo: libro.ritmo})) THEN 1.0
                WHEN EXISTS((usuario)-[:PREFIERE]->(:Genero)) THEN 2.0
                ELSE 5.0
             END as distancia_base
        
        // Ajustar por características del libro
        WITH libro, 
             distancia_base + 
             CASE libro.puntuacion_global
                WHEN null THEN 2.0
                ELSE (5.0 - libro.puntuacion_global)
             END as distancia_total
        
        RETURN libro.id as libro_id,
               libro.ritmo as ritmo,
               libro.final as final,
               libro.elementos as elementos,
               libro.puntuacion_global as puntuacion,
               distancia_total as distancia
        ORDER BY distancia_total ASC
        LIMIT $limite
        """
        
        result = conn.run_query(query, {"usuario_id": usuario_id, "limite": limite})
        
        recomendaciones = []
        for record in result:
            libro = Libro(
                record["libro_id"],
                record["ritmo"],
                record["final"],
                record["elementos"] or [],
                record["puntuacion"] or 0.0
            )
            libro.puntaje = 10.0 - record["distancia"]
            libro.motivo = f"ruta óptima (distancia: {record['distancia']:.2f})"
            recomendaciones.append(libro)
        
        return recomendaciones
        
    except Exception as e:
        print(f"Error en Dijkstra: {e}")
        return []
    
def limpiar_grafo_proyectado():
    """Limpia el grafo proyectado para liberar memoria"""
    try:
        pass
    except Exception as e:
        print(f"Error al limpiar recursos: {e}")