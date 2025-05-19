from database.neo4j_connection import Neo4jConnection

conn = Neo4jConnection("bolt://localhost:7687", "neo4j", "tu_contraseña")

def crear_usuario(usuario):
    query = """
    MERGE (u:Usuario {id: $id})
    SET u.ritmo = $ritmo,
        u.finales = $finales,
        u.elementos = $elementos,
        u.aceptados = $aceptados,
        u.rechazados = $rechazados
    """
    params = {
        "id": usuario.id,
        "ritmo": usuario.ritmo,
        "finales": usuario.finales,
        "elementos": usuario.elementos,
        "aceptados": usuario.aceptados,
        "rechazados": usuario.rechazados
    }
    conn.run_query(query, params)

def crear_libro(libro):
    query = """
    MERGE (l:Libro {id: $id})
    SET l.ritmo = $ritmo,
        l.final = $final,
        l.elementos = $elementos,
        l.puntuacion_global = $puntuacion_global
    """
    params = {
        "id": libro.id,
        "ritmo": libro.ritmo,
        "final": libro.final,
        "elementos": libro.elementos,
        "puntuacion_global": libro.puntuacion_global
    }
    conn.run_query(query, params)

def crear_interaccion(usuario_id, libro_id, tipo):
    query = f"""
    MATCH (u:Usuario {{id: $usuario_id}})
    MATCH (l:Libro {{id: $libro_id}})
    MERGE (u)-[r:{tipo.upper()}]->(l)
    """
    conn.run_query(query, {"usuario_id": usuario_id, "libro_id": libro_id})


# engine/calculo_match.py
def calcular_match(usuario, libro):
    score = 0.0

    if libro.ritmo in usuario.ritmo:
        score += usuario.ritmo[libro.ritmo] * 0.4

    if libro.final in usuario.finales:
        score += usuario.finales[libro.final] * 0.3

    for e in libro.elementos:
        if e in usuario.elementos:
            score += 0.3 / len(usuario.elementos)

    score += libro.puntuacion_global * 0.05

    return score
