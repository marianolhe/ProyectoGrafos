import hashlib
from Connection import Neo4jConnection

# Configuración de la conexión
conn = Neo4jConnection(
    uri="neo4j+s://982b38ec.databases.neo4j.io", 
    user="neo4j",                                 
    pwd="qMIuwlgM9GhNColurgycVECla2yQtyMHgNRSSsnihDI",                           
    db="neo4j"                                    
)

def crear_usuario(usuario):
    """Crea un nuevo usuario en la base de datos"""
    try:
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
        print(f"✅ Usuario {usuario.id} creado exitosamente")
        return True
    except Exception as e:
        print(f"❌ Error creando usuario: {e}")
        return False

def autenticar_usuario(usuario_id, password):
    """Autentica un usuario verificando su contraseña"""
    try:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        query = """
        MATCH (u:Usuario {id: $usuario_id, password: $password_hash})
        RETURN u.id as id
        """
        result = conn.run_query(query, {"usuario_id": usuario_id, "password_hash": password_hash})
        
        if result and len(result) > 0:
            print(f"✅ Usuario {usuario_id} autenticado correctamente")
            return True
        else:
            print(f"❌ Credenciales incorrectas para {usuario_id}")
            return False
    except Exception as e:
        print(f"❌ Error en autenticación: {e}")
        return False

def verificar_usuario_existente(usuario_id):
    """Verifica si un usuario ya existe en la base de datos"""
    try:
        query = "MATCH (u:Usuario {id: $usuario_id}) RETURN u.id as id"
        result = conn.run_query(query, {"usuario_id": usuario_id})
        exists = result and len(result) > 0
        
        if exists:
            print(f"⚠️ Usuario {usuario_id} ya existe")
        else:
            print(f"✅ Usuario {usuario_id} disponible")
        
        return exists
    except Exception as e:
        print(f"❌ Error verificando usuario: {e}")
        return False

def obtener_datos_usuario(usuario_id):
    """Obtiene los datos del usuario desde la base de datos incluyendo géneros"""
    try:
        with conn.driver.session() as session:
            # Obtener datos del usuario
            result = session.run(
                "MATCH (u:Usuario {id: $usuario_id}) RETURN u",
                {"usuario_id": usuario_id}
            )
            record = result.single()
            
            if not record:
                print(f"❌ No se encontraron datos para usuario {usuario_id}")
                return {}
                
            usuario_data = record["u"]
            
            # Obtener géneros que prefiere el usuario
            generos_result = session.run(
                """
                MATCH (u:Usuario {id: $usuario_id})-[:PREFIERE]->(g:Genero)
                RETURN collect(g.nombre) as generos
                """,
                {"usuario_id": usuario_id}
            )
            generos_record = generos_result.single()
            generos = generos_record["generos"] if generos_record else []
            
            # Obtener libros aceptados y rechazados actualizados
            evaluaciones_result = session.run(
                """
                MATCH (u:Usuario {id: $usuario_id})
                OPTIONAL MATCH (u)-[:ACEPTO]->(la:Libro)
                OPTIONAL MATCH (u)-[:RECHAZO]->(lr:Libro)
                RETURN collect(DISTINCT la.id) as aceptados, collect(DISTINCT lr.id) as rechazados
                """,
                {"usuario_id": usuario_id}
            )
            evaluaciones_record = evaluaciones_result.single()
            
            datos = {
                "ritmo": {
                    "rápido": usuario_data.get("ritmo_rapido", 0.0),
                    "lento": usuario_data.get("ritmo_lento", 0.0)
                },
                "finales": {
                    "feliz": usuario_data.get("final_feliz", 0.0),
                    "trágico": usuario_data.get("final_tragico", 0.0)
                },
                "elementos": usuario_data.get("elementos", []),
                "aceptados": evaluaciones_record["aceptados"] if evaluaciones_record else [],
                "rechazados": evaluaciones_record["rechazados"] if evaluaciones_record else [],
                "generos": generos
            }
            
            print(f"✅ Datos recuperados para usuario {usuario_id}")
            return datos
            
    except Exception as e:
        print(f"❌ Error al obtener datos del usuario: {e}")
        return {}

def actualizar_datos_usuario(usuario):
    """Actualiza los datos del usuario en la base de datos"""
    try:
        query = """
        MATCH (u:Usuario {id: $id})
        SET u.ritmo_rapido = $ritmo_rapido,
            u.ritmo_lento = $ritmo_lento,
            u.final_feliz = $final_feliz,
            u.final_tragico = $final_tragico,
            u.elementos = $elementos,
            u.aceptados = $aceptados,
            u.rechazados = $rechazados
        """
        params = {
            "id": usuario.id,
            "ritmo_rapido": usuario.ritmo.get("rápido", 0.0),
            "ritmo_lento": usuario.ritmo.get("lento", 0.0),
            "final_feliz": usuario.finales.get("feliz", 0.0),
            "final_tragico": usuario.finales.get("trágico", 0.0),
            "elementos": usuario.elementos,
            "aceptados": usuario.aceptados,
            "rechazados": usuario.rechazados
        }
        conn.run_query(query, params)
        print(f"✅ Datos actualizados para usuario {usuario.id}")
        return True
    except Exception as e:
        print(f"❌ Error actualizando datos del usuario: {e}")
        return False

def crear_genero(nombre_genero):
    """Crea un género si no existe"""
    try:
        query = "MERGE (g:Genero {nombre: $nombre})"
        conn.run_query(query, {"nombre": nombre_genero})
        print(f"✅ Género '{nombre_genero}' creado/verificado")
        return True
    except Exception as e:
        print(f"❌ Error creando género: {e}")
        return False

def crear_relacion_prefiere(usuario_id, nombre_genero):
    """Crea relación PREFIERE entre usuario y género"""
    try:
        query = """
        MATCH (u:Usuario {id: $usuario_id})
        MATCH (g:Genero {nombre: $nombre_genero})
        MERGE (u)-[:PREFIERE]->(g)
        """
        conn.run_query(query, {"usuario_id": usuario_id, "nombre_genero": nombre_genero})
        print(f"✅ Relación PREFIERE creada: {usuario_id} -> {nombre_genero}")
        return True
    except Exception as e:
        print(f"❌ Error creando relación PREFIERE: {e}")
        return False

def verificar_y_crear_interaccion(usuario_id, libro_id, tipo_interaccion):
    """Verifica y crea una interacción entre usuario y libro"""
    try:
        # Verificar que no exista una interacción previa
        query_verificar = """
        MATCH (u:Usuario {id: $usuario_id})
        MATCH (l:Libro {id: $libro_id})
        OPTIONAL MATCH (u)-[r:ACEPTO|RECHAZO]->(l)
        RETURN r
        """
        result = conn.run_query(query_verificar, {"usuario_id": usuario_id, "libro_id": libro_id})
        
        if result and result[0]["r"] is not None:
            print(f"⚠️ Ya existe una interacción entre {usuario_id} y {libro_id}")
            return False
        
        # Crear la nueva interacción
        query_crear = f"""
        MATCH (u:Usuario {{id: $usuario_id}})
        MATCH (l:Libro {{id: $libro_id}})
        MERGE (u)-[:{tipo_interaccion}]->(l)
        """
        conn.run_query(query_crear, {"usuario_id": usuario_id, "libro_id": libro_id})
        
        print(f"✅ Interacción {tipo_interaccion} creada: {usuario_id} -> {libro_id}")
        return True
        
    except Exception as e:
        print(f"❌ Error creando interacción: {e}")
        return False

def obtener_libros():
    """Obtiene todos los libros de la base de datos"""
    try:
        query = """
        MATCH (l:Libro)
        RETURN l.id as id, 
               l.titulo as titulo,
               l.ritmo as ritmo,
               l.final as final,
               l.elementos as elementos,
               l.puntuacion_global as puntuacion
        ORDER BY l.id
        """
        result = conn.run_query(query)
        
        libros = []
        for record in result:
            libro_data = {
                'id': record['id'],
                'titulo': record['titulo'] or f"Libro {record['id']}",
                'ritmo': record['ritmo'],
                'final': record['final'],
                'elementos': record['elementos'] or [],
                'puntuacion': record['puntuacion'] or 0.0
            }
            libros.append(libro_data)
        
        print(f"✅ Obtenidos {len(libros)} libros de la base de datos")
        return libros
        
    except Exception as e:
        print(f"❌ Error obteniendo libros: {e}")
        return []

def crear_libro(libro_id, titulo, ritmo, final, elementos, puntuacion):
    """Crea un nuevo libro en la base de datos"""
    try:
        query = """
        MERGE (l:Libro {id: $id})
        SET l.titulo = $titulo,
            l.ritmo = $ritmo,
            l.final = $final,
            l.elementos = $elementos,
            l.puntuacion_global = $puntuacion
        """
        params = {
            "id": libro_id,
            "titulo": titulo,
            "ritmo": ritmo,
            "final": final,
            "elementos": elementos,
            "puntuacion": puntuacion
        }
        conn.run_query(query, params)
        print(f"✅ Libro {libro_id} creado exitosamente")
        return True
    except Exception as e:
        print(f"❌ Error creando libro: {e}")
        return False

def obtener_estadisticas_generales():
    """Obtiene estadísticas generales del sistema"""
    try:
        query = """
        MATCH (u:Usuario)
        OPTIONAL MATCH (l:Libro)
        OPTIONAL MATCH ()-[a:ACEPTO]->()
        OPTIONAL MATCH ()-[r:RECHAZO]->()
        RETURN count(DISTINCT u) as total_usuarios,
               count(DISTINCT l) as total_libros,
               count(a) as total_aceptaciones,
               count(r) as total_rechazos
        """
        result = conn.run_query(query)
        
        if result:
            stats = result[0]
            print(f"📊 Estadísticas: {stats['total_usuarios']} usuarios, {stats['total_libros']} libros")
            return {
                'usuarios': stats['total_usuarios'],
                'libros': stats['total_libros'],
                'aceptaciones': stats['total_aceptaciones'],
                'rechazos': stats['total_rechazos']
            }
        else:
            return {'usuarios': 0, 'libros': 0, 'aceptaciones': 0, 'rechazos': 0}
            
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")
        return {'usuarios': 0, 'libros': 0, 'aceptaciones': 0, 'rechazos': 0}

def limpiar_base_datos():
    """Limpia toda la base de datos (usar con precaución)"""
    try:
        query = "MATCH (n) DETACH DELETE n"
        conn.run_query(query)
        print("🧹 Base de datos limpiada completamente")
        return True
    except Exception as e:
        print(f"❌ Error limpiando base de datos: {e}")
        return False

def inicializar_datos_prueba():
    """Inicializa datos de prueba en la base de datos"""
    try:
        # Crear libros de prueba
        libros_prueba = [
            ("L1", "El Misterio de la Casa Antigua", "rápido", "feliz", ["giros", "misterio"], 4.7),
            ("L2", "Amor en Tiempos Perdidos", "lento", "trágico", ["personajes", "romance"], 4.2),
            ("L3", "Guerra de los Mundos Fantásticos", "rápido", "feliz", ["acción", "mundos"], 4.5),
            ("L4", "Secretos del Corazón", "lento", "feliz", ["romance", "personajes"], 4.3),
            ("L5", "Aventuras en el Tiempo", "rápido", "trágico", ["giros", "acción"], 4.6),
            ("L6", "La Última Esperanza", "lento", "trágico", ["personajes", "misterio"], 4.4),
            ("L7", "Mundos Paralelos", "rápido", "feliz", ["mundos", "acción"], 4.8),
            ("L8", "El Jardín de los Suspiros", "lento", "feliz", ["romance", "personajes"], 4.1),
            ("L9", "Cazadores de Sombras", "rápido", "trágico", ["acción", "giros"], 4.9),
            ("L10", "Memorias del Pasado", "lento", "trágico", ["personajes", "misterio"], 4.0)
        ]
        
        for libro_data in libros_prueba:
            crear_libro(*libro_data)
        
        print("✅ Datos de prueba inicializados correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error inicializando datos de prueba: {e}")
        return False

# Función para testing
def test_conexion():
    """Prueba la conexión a la base de datos"""
    try:
        query = "RETURN 'Conexión exitosa' as mensaje"
        result = conn.run_query(query)
        if result:
            print("✅ Conexión a Neo4j exitosa")
            return True
        else:
            print("❌ Error en la conexión")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

if __name__ == "__main__":
    # Ejecutar pruebas básicas
    print("🧪 Probando conexión...")
    test_conexion()
    
    print("\n📊 Obteniendo estadísticas...")
    stats = obtener_estadisticas_generales()
    print(f"Estadísticas actuales: {stats}")