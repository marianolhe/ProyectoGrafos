from Connection import Neo4jConnection
import hashlib

conn = Neo4jConnection("bolt://localhost:7687", "neo4j", "libros123")

def crear_usuario(usuario):
    password_hash = hashlib.sha256(usuario.password.encode()).hexdigest()
    query = """
    MERGE (u:Usuario {id: $id})
    SET u.password = $password,
        u.ritmo_rapido = $ritmo_rapido,
        u.ritmo_lento = $ritmo_lento,
        u.final_feliz = $final_feliz,
        u.final_tragico = $final_tragico,
        u.elementos = $elementos,
        u.aceptados = $aceptados,
        u.rechazados = $rechazados
    """
    params = {
        "id": usuario.id,
        "password": password_hash,
        "ritmo_rapido": usuario.ritmo.get("rápido", 0.0),
        "ritmo_lento": usuario.ritmo.get("lento", 0.0),
        "final_feliz": usuario.finales.get("feliz", 0.0),
        "final_tragico": usuario.finales.get("trágico", 0.0),
        "elementos": usuario.elementos,
        "aceptados": usuario.aceptados,
        "rechazados": usuario.rechazados
    }
    conn.run_query(query, params)

def autenticar_usuario(usuario_id, password):
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    query = """
    MATCH (u:Usuario {id: $usuario_id, password: $password})
    RETURN u LIMIT 1
    """
    result = conn.run_query(query, {"usuario_id": usuario_id, "password": password_hash})
    return result.single() is not None

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

def crear_genero(nombre):
    conn.run_query("MERGE (:Genero {nombre: $nombre})", {"nombre": nombre})

def crear_relacion_prefiere(usuario_id, genero):
    query = """
    MATCH (u:Usuario {id: $id}), (g:Genero {nombre: $genero})
    MERGE (u)-[:PREFIERE]->(g)
    """
    conn.run_query(query, {"id": usuario_id, "genero": genero})

def crear_relacion_posee(libro_id):
    query = """
    MERGE (s:Sistema {id: 'sistema'})
    WITH s
    MATCH (l:Libro {id: $libro_id})
    MERGE (s)-[:POSEE]->(l)
    """
    conn.run_query(query, {"libro_id": libro_id})

def verificar_usuario_existente(usuario_id):
    """Verifica si un usuario con el ID proporcionado ya existe en la base de datos"""
    try:
        with conn.driver.session() as session:
            result = session.run(
                "MATCH (u:Usuario {id: $usuario_id}) RETURN count(u) > 0 as exists",
                {"usuario_id": usuario_id}
            )
            record = result.single()
            return record and record["exists"]
    except Exception as e:
        print(f"Error al verificar usuario: {e}")
        return False

def obtener_datos_usuario(usuario_id):
    """Obtiene los datos del usuario desde la base de datos."""
    query = """
    MATCH (u:Usuario {id: $usuario_id})
    RETURN u
    """
    result = conn.run_query(query, {"usuario_id": usuario_id}).single()
    
    if result:
        usuario_data = result["u"]
        return {
            "ritmo": {
                "rápido": usuario_data.get("ritmo_rapido", 0.0),
                "lento": usuario_data.get("ritmo_lento", 0.0)
            },
            "finales": {
                "feliz": usuario_data.get("final_feliz", 0.0),
                "trágico": usuario_data.get("final_tragico", 0.0)
            },
            "elementos": usuario_data.get("elementos", []),
            "aceptados": usuario_data.get("aceptados", []),
            "rechazados": usuario_data.get("rechazados", [])
        }
    
    return {}