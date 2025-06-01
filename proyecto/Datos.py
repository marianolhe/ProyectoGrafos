from Connection import Neo4jConnection
import hashlib

conn = Neo4jConnection(
    uri="neo4j+s://982b38ec.databases.neo4j.io",
    user="neo4j", 
    pwd="qMIuwlgM9GhNColurgycVECla2yQtyMHgNRSSsnihDI",
    db="neo4j"
)

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
    try:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        with conn.driver.session() as session:
            result = session.run(
                "MATCH (u:Usuario {id: $usuario_id, password: $password}) RETURN count(u) > 0 as exists",
                {"usuario_id": usuario_id, "password": password_hash}
            )
            record = result.single()
            return record and record["exists"]
    except Exception as e:
        print(f"Error al autenticar usuario: {e}")
        return False

def crear_libro(libro):
    query = """
    MERGE (l:Libro {id: $id})
    SET l.titulo = $titulo,
        l.ritmo = $ritmo,
        l.final = $final,
        l.elementos = $elementos,
        l.puntuacion_global = $puntuacion_global
    """
    params = {
        "id": libro.id,
        "titulo": libro.titulo,  # ← AGREGAR título
        "ritmo": libro.ritmo,
        "final": libro.final,
        "elementos": libro.elementos,
        "puntuacion_global": libro.puntuacion_global
    }
    conn.run_query(query, params)

def verificar_y_crear_interaccion(usuario_id, libro_id, tipo):
    """Verifica que los nodos existan y luego crea la relación"""
    try:
        with conn.driver.session() as session:
            # Primero verificar que ambos nodos existen
            verificacion = session.run(
                """
                OPTIONAL MATCH (u:Usuario {id: $usuario_id})
                OPTIONAL MATCH (l:Libro {id: $libro_id})
                RETURN u IS NOT NULL as usuario_existe, l IS NOT NULL as libro_existe
                """,
                {"usuario_id": usuario_id, "libro_id": libro_id}
            ).single()
            
            if not verificacion["usuario_existe"]:
                print(f"ERROR: El usuario {usuario_id} no existe en la base de datos")
                return False
                
            if not verificacion["libro_existe"]:
                print(f"ERROR: El libro {libro_id} no existe en la base de datos")
                return False
            
            # Si ambos existen, crear la relación
            result = session.run(
                f"""
                MATCH (u:Usuario {{id: $usuario_id}})
                MATCH (l:Libro {{id: $libro_id}})
                MERGE (u)-[r:{tipo.upper()}]->(l)
                RETURN count(r) as relacion_creada
                """,
                {"usuario_id": usuario_id, "libro_id": libro_id}
            ).single()
            
            print(f"Relación {tipo} creada exitosamente")
            return True
            
    except Exception as e:
        print(f"ERROR al procesar interacción: {e}")
        return False

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
    try:
        with conn.driver.session() as session:
            result = session.run(
                "MATCH (u:Usuario {id: $usuario_id}) RETURN u",
                {"usuario_id": usuario_id}
            )
            record = result.single()
            
            if not record:
                return {}
                
            usuario_data = record["u"]
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
    except Exception as e:
        print(f"Error al obtener datos del usuario: {e}")
        return {}