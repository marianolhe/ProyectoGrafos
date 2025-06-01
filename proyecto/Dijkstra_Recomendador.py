from Connection import Neo4jConnection
from Libro import Libro

conn = Neo4jConnection(
    uri="neo4j+s://982b38ec.databases.neo4j.io", 
    user="neo4j",                                 
    pwd="qMIuwlgM9GhNColurgycVECla2yQtyMHgNRSSsnihDI",                           
    db="neo4j"                                    
)

def recomendar_con_dijkstra(usuario_id, limite=5):
    """Algoritmo de Dijkstra simulado para recomendaciones inteligentes"""
    try:
        print(f"🔍 Iniciando recomendaciones Dijkstra para usuario: {usuario_id}")
        
        # Verificar si el usuario tiene evaluaciones previas
        query_evaluaciones = """
        MATCH (u:Usuario {id: $usuario_id})
        OPTIONAL MATCH (u)-[:ACEPTO]->(libros_aceptados:Libro)
        OPTIONAL MATCH (u)-[:RECHAZO]->(libros_rechazados:Libro)
        RETURN count(libros_aceptados) as aceptados, count(libros_rechazados) as rechazados
        """
        
        evaluaciones = conn.run_query(query_evaluaciones, {"usuario_id": usuario_id})
        if evaluaciones:
            aceptados = evaluaciones[0]["aceptados"]
            rechazados = evaluaciones[0]["rechazados"]
            print(f"📊 Usuario tiene {aceptados} libros aceptados y {rechazados} rechazados")
        
        # Algoritmo principal de Dijkstra simulado
        query_dijkstra = """
        MATCH (usuario_actual:Usuario {id: $usuario_id})
        
        // PASO 1: Encontrar usuarios similares (Dijkstra - cálculo de distancias)
        MATCH (otros_usuarios:Usuario)
        WHERE otros_usuarios.id <> $usuario_id
        
        // Calcular libros en común (aceptados)
        OPTIONAL MATCH (usuario_actual)-[:ACEPTO]->(libro_comun:Libro)<-[:ACEPTO]-(otros_usuarios)
        
        // Calcular libros rechazados en común
        OPTIONAL MATCH (usuario_actual)-[:RECHAZO]->(libro_rechazo_comun:Libro)<-[:RECHAZO]-(otros_usuarios)
        
        WITH usuario_actual, otros_usuarios, 
             count(DISTINCT libro_comun) AS libros_aceptados_comun,
             count(DISTINCT libro_rechazo_comun) AS libros_rechazados_comun,
             // Calcular similitud en preferencias numéricas
             abs(coalesce(usuario_actual.ritmo_rapido, 0.5) - coalesce(otros_usuarios.ritmo_rapido, 0.5)) + 
             abs(coalesce(usuario_actual.ritmo_lento, 0.5) - coalesce(otros_usuarios.ritmo_lento, 0.5)) +
             abs(coalesce(usuario_actual.final_feliz, 0.5) - coalesce(otros_usuarios.final_feliz, 0.5)) + 
             abs(coalesce(usuario_actual.final_tragico, 0.5) - coalesce(otros_usuarios.final_tragico, 0.5)) AS diferencia_preferencias
        
        // PASO 2: Calcular "distancia Dijkstra" entre usuarios
        WITH otros_usuarios, 
             // Fórmula de distancia: menor distancia = usuarios más similares
             CASE 
                WHEN libros_aceptados_comun > 0 OR libros_rechazados_comun > 0 
                THEN (2.0 / (1.0 + libros_aceptados_comun + libros_rechazados_comun)) + (diferencia_preferencias / 4.0)
                ELSE 3.0 + (diferencia_preferencias / 2.0)
             END AS distancia_dijkstra,
             libros_aceptados_comun,
             libros_rechazados_comun
        
        WHERE distancia_dijkstra < 4.0  // Solo usuarios "cercanos" en el grafo
        ORDER BY distancia_dijkstra ASC
        LIMIT 8  // Los 8 usuarios más similares
        
        // PASO 3: Encontrar libros recomendados a través de "rutas cortas"
        MATCH (otros_usuarios)-[:ACEPTO]->(libro_recomendado:Libro)
        WHERE NOT EXISTS((:Usuario {id: $usuario_id})-[:ACEPTO|RECHAZO]->(libro_recomendado))
        
        // PASO 4: Calcular puntuación final considerando múltiples factores
        MATCH (usuario_actual:Usuario {id: $usuario_id})
        WITH libro_recomendado, distancia_dijkstra, usuario_actual, otros_usuarios,
             libros_aceptados_comun, libros_rechazados_comun,
             
             // Bonus por compatibilidad personal con preferencias del usuario
             CASE 
                WHEN libro_recomendado.ritmo = 'rápido' AND coalesce(usuario_actual.ritmo_rapido, 0.5) > 0.6 THEN 2.5
                WHEN libro_recomendado.ritmo = 'lento' AND coalesce(usuario_actual.ritmo_lento, 0.5) > 0.6 THEN 2.5
                WHEN libro_recomendado.ritmo = 'rápido' AND coalesce(usuario_actual.ritmo_rapido, 0.5) < 0.3 THEN -1.0
                WHEN libro_recomendado.ritmo = 'lento' AND coalesce(usuario_actual.ritmo_lento, 0.5) < 0.3 THEN -1.0
                ELSE 0.5
             END +
             CASE
                WHEN libro_recomendado.final = 'feliz' AND coalesce(usuario_actual.final_feliz, 0.5) > 0.6 THEN 2.0
                WHEN libro_recomendado.final = 'trágico' AND coalesce(usuario_actual.final_tragico, 0.5) > 0.6 THEN 2.0
                WHEN libro_recomendado.final = 'feliz' AND coalesce(usuario_actual.final_tragico, 0.5) > 0.7 THEN -0.5
                WHEN libro_recomendado.final = 'trágico' AND coalesce(usuario_actual.final_feliz, 0.5) > 0.7 THEN -0.5
                ELSE 0.3
             END +
             CASE
                WHEN any(elem IN coalesce(libro_recomendado.elementos, []) WHERE elem IN coalesce(usuario_actual.elementos, [])) THEN 1.5
                ELSE 0.0
             END AS bonus_compatibilidad_personal
        
        // *** CAMBIO 1: Limitar puntuación final a máximo 10.0 ***
        WITH libro_recomendado, distancia_dijkstra, libros_aceptados_comun, otros_usuarios,
             // Componente principal: similitud de usuarios (inverso de distancia Dijkstra)
             CASE 
                WHEN (3.0 / (1.0 + distancia_dijkstra)) + bonus_compatibilidad_personal + (coalesce(libro_recomendado.puntuacion_global, 3.0) * 0.8) > 10.0 
                THEN 10.0
                ELSE (3.0 / (1.0 + distancia_dijkstra)) + bonus_compatibilidad_personal + (coalesce(libro_recomendado.puntuacion_global, 3.0) * 0.8)
             END AS puntuacion_final,
             
             // Generar motivo explicativo
             CASE 
                WHEN distancia_dijkstra < 1.8 AND libros_aceptados_comun > 2 
                THEN 'usuarios con gustos prácticamente idénticos aman este libro'
                WHEN distancia_dijkstra < 2.5 AND libros_aceptados_comun > 1 
                THEN 'usuarios muy similares a ti lo recomiendan altamente'
                WHEN bonus_compatibilidad_personal > 3.5 
                THEN 'coincide perfectamente con todas tus preferencias'
                WHEN bonus_compatibilidad_personal > 2.0 
                THEN 'excelente match con tus gustos personales'
                WHEN libro_recomendado.puntuacion_global > 4.5 
                THEN 'obra maestra recomendada por la comunidad literaria'
                WHEN distancia_dijkstra < 3.0 
                THEN 'descubrimiento basado en patrones de usuarios similares'
                ELSE 'nueva experiencia literaria cuidadosamente seleccionada'
             END AS motivo
        
        // *** CAMBIO 2: Recopilar usuarios que recomiendan específicamente ***
        WITH libro_recomendado, 
             avg(puntuacion_final) AS puntuacion_promedio,
             collect(DISTINCT motivo)[0] AS motivo_principal,
             count(DISTINCT otros_usuarios) AS total_usuarios_recomiendan,
             collect(DISTINCT otros_usuarios.id)[0..3] AS usuarios_que_recomiendan_nombres  // Máximo 3 nombres
        
        RETURN DISTINCT libro_recomendado.id as libro_id,
               coalesce(libro_recomendado.titulo, 'Libro ' + libro_recomendado.id) as titulo,
               libro_recomendado.ritmo as ritmo,
               libro_recomendado.final as final,
               coalesce(libro_recomendado.elementos, []) as elementos,
               coalesce(libro_recomendado.puntuacion_global, 0.0) as puntuacion,
               puntuacion_promedio as puntaje,
               motivo_principal as motivo,
               total_usuarios_recomiendan,
               usuarios_que_recomiendan_nombres
        ORDER BY puntuacion_promedio DESC, total_usuarios_recomiendan DESC
        LIMIT $limite
        """
        
        result = conn.run_query(query_dijkstra, {"usuario_id": usuario_id, "limite": limite})
        
        if not result:
            print("⚠️ No se encontraron recomendaciones con Dijkstra, usando algoritmo de respaldo")
            return algoritmo_respaldo(usuario_id, limite)
        
        # Crear objetos Libro con recomendaciones
        recomendaciones = []
        for record in result:
            libro = Libro(
                record["libro_id"],
                record["ritmo"],
                record["final"],
                record["elementos"],
                record["puntuacion"],
                record["titulo"]
            )
            libro.puntaje = round(min(10.0, record["puntaje"]), 2)  # *** ASEGURAR máximo 10.0 ***
            libro.motivo = record["motivo"]
            libro.usuarios_recomiendan = record["total_usuarios_recomiendan"]
            libro.nombres_usuarios_recomiendan = record["usuarios_que_recomiendan_nombres"] or []
            recomendaciones.append(libro)
        
        print(f"✅ Generadas {len(recomendaciones)} recomendaciones con Dijkstra")
        return recomendaciones
        
    except Exception as e:
        print(f"❌ Error en Dijkstra: {e}")
        return algoritmo_respaldo(usuario_id, limite)

def algoritmo_respaldo(usuario_id, limite=5):
    """Algoritmo de respaldo cuando no hay suficientes datos para Dijkstra"""
    try:
        print(f"🔄 Ejecutando algoritmo de respaldo para {usuario_id}")
        
        query_respaldo = """
        MATCH (usuario:Usuario {id: $usuario_id})
        
        // Buscar libros no evaluados
        MATCH (libro_candidato:Libro)
        WHERE NOT EXISTS((usuario)-[:ACEPTO|RECHAZO]->(libro_candidato))
        
        // Calcular compatibilidad basada en preferencias del usuario
        WITH usuario, libro_candidato,
             CASE 
                WHEN libro_candidato.ritmo = 'rápido' AND coalesce(usuario.ritmo_rapido, 0.5) > 0.5 THEN 2.0
                WHEN libro_candidato.ritmo = 'lento' AND coalesce(usuario.ritmo_lento, 0.5) > 0.5 THEN 2.0
                ELSE 0.8
             END +
             CASE
                WHEN libro_candidato.final = 'feliz' AND coalesce(usuario.final_feliz, 0.5) > 0.5 THEN 1.5
                WHEN libro_candidato.final = 'trágico' AND coalesce(usuario.final_tragico, 0.5) > 0.5 THEN 1.5
                ELSE 0.5
             END +
             CASE
                WHEN any(elem IN coalesce(libro_candidato.elementos, []) WHERE elem IN coalesce(usuario.elementos, [])) THEN 1.5
                ELSE 0.0
             END +
             coalesce(libro_candidato.puntuacion_global, 3.0) AS puntuacion_total
        
        // *** CAMBIO 1: Limitar a 10.0 en algoritmo de respaldo también ***
        WITH libro_candidato, 
             CASE WHEN puntuacion_total > 10.0 THEN 10.0 ELSE puntuacion_total END AS puntuacion_final,
             CASE 
                WHEN puntuacion_total > 8.0 THEN 'excelente match con tus preferencias iniciales'
                WHEN puntuacion_total > 6.0 THEN 'buena compatibilidad con tu perfil'
                WHEN libro_candidato.puntuacion_global > 4.5 THEN 'libro destacado por la comunidad'
                ELSE 'recomendación para explorar nuevos horizontes'
             END AS motivo
        
        RETURN libro_candidato.id as libro_id,
               coalesce(libro_candidato.titulo, 'Libro ' + libro_candidato.id) as titulo,
               libro_candidato.ritmo as ritmo,
               libro_candidato.final as final,
               coalesce(libro_candidato.elementos, []) as elementos,
               coalesce(libro_candidato.puntuacion_global, 0.0) as puntuacion,
               puntuacion_final as puntaje,
               motivo
        ORDER BY puntuacion_final DESC
        LIMIT $limite
        """
        
        result = conn.run_query(query_respaldo, {"usuario_id": usuario_id, "limite": limite})
        
        recomendaciones = []
        for record in result:
            libro = Libro(
                record["libro_id"],
                record["ritmo"],
                record["final"],
                record["elementos"],
                record["puntuacion"],
                record["titulo"]
            )
            libro.puntaje = round(min(10.0, record["puntaje"]), 2)  # *** ASEGURAR máximo 10.0 ***
            libro.motivo = record["motivo"]
            libro.nombres_usuarios_recomiendan = []  # Vacío para respaldo
            recomendaciones.append(libro)
        
        print(f"✅ Generadas {len(recomendaciones)} recomendaciones de respaldo")
        return recomendaciones
        
    except Exception as e:
        print(f"❌ Error en algoritmo de respaldo: {e}")
        return []

# *** RESTO DEL CÓDIGO IGUAL ***
def crear_usuarios_de_prueba():
    """Crear usuarios de prueba para demostrar el funcionamiento de Dijkstra"""
    try:
        usuarios_prueba = """
        // Crear usuarios de prueba con diferentes perfiles
        MERGE (u1:Usuario {id: 'alice'})
        SET u1.password = 'hash_alice',
            u1.ritmo_rapido = 0.8, u1.ritmo_lento = 0.2,
            u1.final_feliz = 0.7, u1.final_tragico = 0.3,
            u1.elementos = ['acción', 'giros']
            
        MERGE (u2:Usuario {id: 'bob'})
        SET u2.password = 'hash_bob',
            u2.ritmo_rapido = 0.9, u2.ritmo_lento = 0.1,
            u2.final_feliz = 0.8, u2.final_tragico = 0.2,
            u2.elementos = ['acción', 'mundos']
            
        MERGE (u3:Usuario {id: 'carol'})
        SET u3.password = 'hash_carol',
            u3.ritmo_rapido = 0.3, u3.ritmo_lento = 0.7,
            u3.final_feliz = 0.2, u3.final_tragico = 0.8,
            u3.elementos = ['personajes', 'romance']
            
        // Crear interacciones de prueba
        MERGE (u1)-[:ACEPTO]->(:Libro {id: 'L1'})
        MERGE (u1)-[:ACEPTO]->(:Libro {id: 'L3'})
        MERGE (u1)-[:ACEPTO]->(:Libro {id: 'L5'})
        
        MERGE (u2)-[:ACEPTO]->(:Libro {id: 'L1'})
        MERGE (u2)-[:ACEPTO]->(:Libro {id: 'L3'})
        MERGE (u2)-[:ACEPTO]->(:Libro {id: 'L7'})
        
        MERGE (u3)-[:ACEPTO]->(:Libro {id: 'L2'})
        MERGE (u3)-[:ACEPTO]->(:Libro {id: 'L4'})
        MERGE (u3)-[:RECHAZO]->(:Libro {id: 'L1'})
        """
        
        conn.run_query(usuarios_prueba)
        print("✅ Usuarios de prueba creados exitosamente")
        
    except Exception as e:
        print(f"❌ Error creando usuarios de prueba: {e}")

def limpiar_grafo_proyectado():
    """Limpia recursos temporales"""
    try:
        # En esta implementación no necesitamos limpiar grafos proyectados
        print("🧹 Recursos limpiados")
    except Exception as e:
        print(f"Error limpiando recursos: {e}")