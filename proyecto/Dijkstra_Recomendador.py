from Connection import Neo4jConnection
from Libro import Libro

conn = Neo4jConnection(
    uri="neo4j+s://982b38ec.databases.neo4j.io", 
    user="neo4j",                                 
    pwd="qMIuwlgM9GhNColurgycVECla2yQtyMHgNRSSsnihDI",                           
    db="neo4j"                                    
)

def recomendar_con_dijkstra(usuario_id, limite=5):
    try:
        query = """
        MATCH (usuario:Usuario {id: $usuario_id})
        MATCH (libro:Libro)
        WHERE NOT EXISTS((usuario)-[:ACEPTO|RECHAZO]->(libro))
        
        // Calcular compatibilidad basada en preferencias del usuario
        WITH libro, usuario,
             CASE 
                WHEN libro.ritmo = usuario.ritmo_preferido THEN 3
                ELSE 0
             END + 
             CASE 
                WHEN libro.final = usuario.final_preferido THEN 2
                ELSE 0
             END +
             CASE 
                WHEN any(elem IN libro.elementos WHERE elem IN usuario.elementos) THEN 2
                ELSE 0
             END as puntuacion_match
        
        // Calcular motivo de recomendación
        WITH libro, puntuacion_match,
             CASE 
                WHEN libro.ritmo = usuario.ritmo_preferido 
                THEN 'coincide con tu ritmo de lectura preferido'
                WHEN libro.final = usuario.final_preferido 
                THEN 'tiene el tipo de final que prefieres'
                WHEN any(elem IN libro.elementos WHERE elem IN usuario.elementos)
                THEN 'contiene elementos narrativos que te gustan'
                ELSE 'podría interesarte por sus características'
             END as motivo
        
        RETURN libro.id as libro_id,
               libro.titulo as titulo,
               libro.ritmo as ritmo,
               libro.final as final,
               libro.elementos as elementos,
               libro.puntuacion_global as puntuacion,
               puntuacion_match as puntaje,
               motivo
        ORDER BY puntuacion_match DESC
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
                record["puntuacion"] or 0.0,
                record["titulo"]
            )
            libro.puntaje = record["puntaje"]
            libro.motivo = record["motivo"]
            recomendaciones.append(libro)
        
        return recomendaciones
        
    except Exception as e:
        print(f"Error en recomendaciones: {e}")
        return []
    
def limpiar_grafo_proyectado():
    """Limpia el grafo proyectado para liberar memoria"""
    try:
        pass
    except Exception as e:
        print(f"Error al limpiar recursos: {e}")