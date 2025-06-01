from Usuario import Usuario
from Libro import Libro
from Dijkstra_Recomendador import recomendar_con_dijkstra, limpiar_grafo_proyectado
from Datos import crear_usuario, verificar_y_crear_interaccion, autenticar_usuario, verificar_usuario_existente, crear_genero, crear_relacion_prefiere, obtener_datos_usuario, actualizar_datos_usuario

class SistemaRecomendacion:
    def __init__(self):
        self.usuario_actual = None
        self.libros_sistema = []
        self.historial_recomendaciones = []
        self.cache_evaluaciones = {}  # Cache para mejorar rendimiento
        self._inicializar_libros_predeterminados()
    
    def _inicializar_libros_predeterminados(self):
        """Carga libros existentes desde la base de datos"""
        try:
            from Datos import conn
            query = "MATCH (l:Libro) RETURN l.id, l.titulo, l.ritmo, l.final, l.elementos, l.puntuacion_global ORDER BY l.id"
            result = conn.run_query(query)
            
            self.libros_sistema = []
            for record in result:
                libro = Libro(
                    record["l.id"],
                    record["l.ritmo"],
                    record["l.final"], 
                    record["l.elementos"] or [],
                    record["l.puntuacion_global"] or 0.0,
                    record["l.titulo"] or f"Libro {record['l.id']}"
                )
                self.libros_sistema.append(libro)
                
            print(f"✅ Cargados {len(self.libros_sistema)} libros desde la base de datos")
            
        except Exception as e:
            print(f"Error cargando libros: {e}")
            # Mantener libros básicos si hay error
            libro1 = Libro("L1", "rápido", "feliz", ["giros"], 4.7, "El Misterio de la Casa Antigua")
            libro2 = Libro("L2", "lento", "trágico", ["personajes"], 4.2, "Amor en Tiempos Perdidos")
            libro3 = Libro("L3", "rápido", "feliz", ["acción"], 4.5, "Guerra de los Mundos Fantásticos")
            libro4 = Libro("L4", "lento", "feliz", ["romance"], 4.3, "Secretos del Corazón")
            libro5 = Libro("L5", "rápido", "trágico", ["giros"], 4.6, "Aventuras en el Tiempo")
            self.libros_sistema = [libro1, libro2, libro3, libro4, libro5]
    
    def registrar_nuevo_usuario(self, usuario_id, password, generos, ritmo_op, final_op, elementos):
        """Registra un nuevo usuario en el sistema"""
        try:
            # Validar que el usuario no exista
            if verificar_usuario_existente(usuario_id):
                return False, "El ID de usuario ya existe"
            
            # Validar campos requeridos
            if not usuario_id or not password:
                return False, "ID de usuario y contraseña son requeridos"
            
            if len(generos) == 0:
                return False, "Debes seleccionar al menos un género"
            
            # Procesar preferencias
            ritmo = {"rápido": 1.0 if ritmo_op == "rápido" else 0.0,
                    "lento": 1.0 if ritmo_op == "lento" else 0.0}
            
            finales = {"feliz": 1.0 if final_op == "felices" else 0.0,
                      "trágico": 1.0 if final_op == "trágicos" else 0.0}
            
            # Crear objeto usuario
            usuario = Usuario(
                id=usuario_id,
                password=password,
                ritmo=ritmo,
                finales=finales,
                elementos=elementos
            )
            
            # Guardar en base de datos
            crear_usuario(usuario)
            for genero in generos:
                crear_genero(genero)
                crear_relacion_prefiere(usuario_id, genero)
            
            self.usuario_actual = usuario
            # Agregar géneros al objeto usuario
            self.usuario_actual.generos = generos
            
            return True, f"Usuario {usuario_id} creado exitosamente"
            
        except Exception as e:
            return False, f"Error al crear usuario: {e}"
    
    def autenticar_usuario(self, usuario_id, password):
        """Autentica un usuario y carga sus datos"""
        try:
            if not usuario_id or not password:
                return False, "ID de usuario y contraseña son requeridos"
            
            from Datos import autenticar_usuario as auth_func
            if auth_func(usuario_id, password):
                # Obtener datos del usuario
                datos_usuario = obtener_datos_usuario(usuario_id)
                
                if not datos_usuario:
                    # Valores predeterminados si no se pueden recuperar datos
                    datos_usuario = {
                        "ritmo": {"rápido": 0.5, "lento": 0.5},
                        "finales": {"feliz": 0.5, "trágico": 0.5},
                        "elementos": [],
                        "aceptados": [],
                        "rechazados": [],
                        "generos": []
                    }
                
                # Crear objeto usuario con datos recuperados
                self.usuario_actual = Usuario(
                    id=usuario_id,
                    password=password,
                    ritmo=datos_usuario.get("ritmo", {"rápido": 0.0, "lento": 0.0}),
                    finales=datos_usuario.get("finales", {"feliz": 0.0, "trágico": 0.0}),
                    elementos=datos_usuario.get("elementos", []),
                    aceptados=datos_usuario.get("aceptados", []),
                    rechazados=datos_usuario.get("rechazados", [])
                )
                
                # Agregar géneros al objeto usuario
                self.usuario_actual.generos = datos_usuario.get("generos", [])
                
                # Limpiar cache
                self.cache_evaluaciones = {}
                
                return True, f"Bienvenido de nuevo, {usuario_id}!"
            else:
                return False, "ID de usuario o contraseña incorrectos"
                
        except Exception as e:
            return False, f"Error de autenticación: {e}"
    
    def evaluar_libro(self, libro_id, acepta):
        """Registra la evaluación de un libro por parte del usuario"""
        try:
            if not self.usuario_actual:
                return False, "No hay usuario autenticado"
            
            # Verificar que el libro no haya sido evaluado previamente
            if libro_id in self.usuario_actual.aceptados or libro_id in self.usuario_actual.rechazados:
                return False, "Este libro ya ha sido evaluado"
            
            tipo_interaccion = "ACEPTO" if acepta else "RECHAZO"
            exito = verificar_y_crear_interaccion(self.usuario_actual.id, libro_id, tipo_interaccion)
            
            if exito:
                # Actualizar listas locales del usuario
                if acepta:
                    if libro_id not in self.usuario_actual.aceptados:
                        self.usuario_actual.aceptados.append(libro_id)
                else:
                    if libro_id not in self.usuario_actual.rechazados:
                        self.usuario_actual.rechazados.append(libro_id)
                
                # Actualizar preferencias del usuario basándose en la evaluación
                self._actualizar_preferencias_usuario(libro_id, acepta)
                
                # Guardar cambios en la base de datos
                actualizar_datos_usuario(self.usuario_actual)
                
                # Limpiar cache de evaluaciones
                self.cache_evaluaciones = {}
                
                accion = "aceptado" if acepta else "rechazado"
                return True, f"Libro {accion} exitosamente"
            else:
                return False, "Error al registrar la evaluación en la base de datos"
                
        except Exception as e:
            return False, f"Error al evaluar libro: {e}"
    
    def _actualizar_preferencias_usuario(self, libro_id, acepta):
        """Actualiza las preferencias del usuario basándose en sus evaluaciones"""
        try:
            # Encontrar el libro evaluado
            libro = next((l for l in self.libros_sistema if l.id == libro_id), None)
            if not libro:
                return
            
            # Factor de aprendizaje (qué tanto influye cada evaluación)
            factor = 0.1 if acepta else -0.05
            
            # Actualizar preferencias de ritmo
            if libro.ritmo == "rápido":
                self.usuario_actual.ritmo["rápido"] = min(1.0, max(0.0, 
                    self.usuario_actual.ritmo["rápido"] + factor))
                self.usuario_actual.ritmo["lento"] = min(1.0, max(0.0, 
                    self.usuario_actual.ritmo["lento"] - factor/2))
            elif libro.ritmo == "lento":
                self.usuario_actual.ritmo["lento"] = min(1.0, max(0.0, 
                    self.usuario_actual.ritmo["lento"] + factor))
                self.usuario_actual.ritmo["rápido"] = min(1.0, max(0.0, 
                    self.usuario_actual.ritmo["rápido"] - factor/2))
            
            # Actualizar preferencias de final
            if libro.final == "feliz":
                self.usuario_actual.finales["feliz"] = min(1.0, max(0.0, 
                    self.usuario_actual.finales["feliz"] + factor))
                self.usuario_actual.finales["trágico"] = min(1.0, max(0.0, 
                    self.usuario_actual.finales["trágico"] - factor/2))
            elif libro.final == "trágico":
                self.usuario_actual.finales["trágico"] = min(1.0, max(0.0, 
                    self.usuario_actual.finales["trágico"] + factor))
                self.usuario_actual.finales["feliz"] = min(1.0, max(0.0, 
                    self.usuario_actual.finales["feliz"] - factor/2))
            
            # Actualizar elementos preferidos
            if acepta:
                for elemento in libro.elementos:
                    if elemento not in self.usuario_actual.elementos:
                        self.usuario_actual.elementos.append(elemento)
            else:
                # Si rechaza, reducir la preferencia por elementos del libro
                for elemento in libro.elementos:
                    if elemento in self.usuario_actual.elementos and len(self.usuario_actual.elementos) > 1:
                        # Solo remover si tiene más de un elemento preferido
                        import random
                        if random.random() < 0.3:  # 30% de probabilidad de remover
                            self.usuario_actual.elementos.remove(elemento)
            
            print(f"🧠 Preferencias actualizadas para {self.usuario_actual.id}")
            
        except Exception as e:
            print(f"Error actualizando preferencias: {e}")
    
    def obtener_libros_para_evaluar(self):
        """Obtiene libros inteligentemente para evaluación aleatoria pero acorde a preferencias"""
        if not self.usuario_actual:
            return []
        
        # Usar cache si está disponible
        cache_key = f"{self.usuario_actual.id}_libros_evaluar"
        if cache_key in self.cache_evaluaciones:
            return self.cache_evaluaciones[cache_key]
        
        try:
            # Obtener libros usando algoritmo inteligente de selección
            from Datos import conn
            
            query_libros_inteligentes = """
            MATCH (usuario:Usuario {id: $usuario_id})
            MATCH (libro:Libro)
            WHERE NOT EXISTS((usuario)-[:ACEPTO|RECHAZO]->(libro))
            
            // Calcular score de compatibilidad para priorizar
            WITH usuario, libro,
                 // Score basado en preferencias del usuario
                 CASE 
                    WHEN libro.ritmo = 'rápido' AND coalesce(usuario.ritmo_rapido, 0.5) > 0.5 THEN 3.0
                    WHEN libro.ritmo = 'lento' AND coalesce(usuario.ritmo_lento, 0.5) > 0.5 THEN 3.0
                    ELSE 1.0
                 END +
                 CASE
                    WHEN libro.final = 'feliz' AND coalesce(usuario.final_feliz, 0.5) > 0.5 THEN 2.0
                    WHEN libro.final = 'trágico' AND coalesce(usuario.final_tragico, 0.5) > 0.5 THEN 2.0
                    ELSE 0.5
                 END +
                 CASE
                    WHEN any(elem IN coalesce(libro.elementos, []) WHERE elem IN coalesce(usuario.elementos, [])) THEN 2.0
                    ELSE 0.0
                 END +
                 // Factor aleatorio para variar el orden
                 rand() * 2.0 AS score_evaluacion
            
            // Mezclar libros compatibles con algunos aleatorios
            WITH libro, score_evaluacion,
                 CASE 
                    WHEN score_evaluacion > 5.0 THEN 'alta_compatibilidad'
                    WHEN score_evaluacion > 3.0 THEN 'media_compatibilidad' 
                    ELSE 'exploratoria'
                 END AS categoria
            
            // Devolver mix: 60% compatibles, 40% exploratorios
            WITH libro, score_evaluacion, categoria,
                 CASE 
                    WHEN categoria = 'alta_compatibilidad' THEN score_evaluacion + 10.0
                    WHEN categoria = 'media_compatibilidad' THEN score_evaluacion + 5.0
                    ELSE score_evaluacion
                 END AS score_final
            
            RETURN libro.id as libro_id,
                   coalesce(libro.titulo, 'Libro ' + libro.id) as titulo,
                   libro.ritmo as ritmo,
                   libro.final as final,
                   coalesce(libro.elementos, []) as elementos,
                   coalesce(libro.puntuacion_global, 0.0) as puntuacion_global,
                   score_final,
                   categoria
            ORDER BY score_final DESC, rand()  // Ordenar por compatibilidad pero con factor aleatorio
            LIMIT 20  // Obtener pool más grande para mejor selección
            """
            
            result = conn.run_query(query_libros_inteligentes, {"usuario_id": self.usuario_actual.id})
            
            # Convertir a objetos Libro
            libros_candidatos = []
            for record in result:
                libro = Libro(
                    record["libro_id"],
                    record["ritmo"],
                    record["final"],
                    record["elementos"],
                    record["puntuacion_global"],
                    record["titulo"]
                )
                libro.categoria_evaluacion = record["categoria"]
                libro.score_evaluacion = record["score_final"]
                libros_candidatos.append(libro)
            
            # Si no hay libros en BD, usar libros del sistema local como respaldo
            if not libros_candidatos:
                libros_candidatos = [
                    libro for libro in self.libros_sistema 
                    if libro.id not in (self.usuario_actual.aceptados + self.usuario_actual.rechazados)
                ]
                
                # Aplicar orden inteligente local
                import random
                
                def calcular_compatibilidad_local(libro):
                    score = 0.0
                    
                    # Compatibilidad de ritmo
                    if libro.ritmo == "rápido" and self.usuario_actual.ritmo.get("rápido", 0.5) > 0.5:
                        score += 3.0
                    elif libro.ritmo == "lento" and self.usuario_actual.ritmo.get("lento", 0.5) > 0.5:
                        score += 3.0
                    else:
                        score += 1.0
                    
                    # Compatibilidad de final
                    if libro.final == "feliz" and self.usuario_actual.finales.get("feliz", 0.5) > 0.5:
                        score += 2.0
                    elif libro.final == "trágico" and self.usuario_actual.finales.get("trágico", 0.5) > 0.5:
                        score += 2.0
                    else:
                        score += 0.5
                    
                    # Compatibilidad de elementos
                    elementos_comunes = set(libro.elementos) & set(self.usuario_actual.elementos)
                    if elementos_comunes:
                        score += 2.0
                    
                    # Factor aleatorio
                    score += random.uniform(0, 2.0)
                    
                    return score
                
                # Ordenar por compatibilidad + aleatoriedad
                libros_candidatos.sort(key=calcular_compatibilidad_local, reverse=True)
                
                # Asignar categorías localmente
                for i, libro in enumerate(libros_candidatos):
                    if i < len(libros_candidatos) * 0.4:  # 40% alta compatibilidad
                        libro.categoria_evaluacion = 'alta_compatibilidad'
                    elif i < len(libros_candidatos) * 0.7:  # 30% media compatibilidad
                        libro.categoria_evaluacion = 'media_compatibilidad'
                    else:  # 30% exploratoria
                        libro.categoria_evaluacion = 'exploratoria'
            
            # Guardar en cache
            self.cache_evaluaciones[cache_key] = libros_candidatos
            
            print(f"📚 Seleccionados {len(libros_candidatos)} libros para evaluación inteligente")
            return libros_candidatos
            
        except Exception as e:
            print(f"Error obteniendo libros para evaluar: {e}")
            # Respaldo simple en caso de error
            libros_respaldo = [
                libro for libro in self.libros_sistema 
                if libro.id not in (self.usuario_actual.aceptados + self.usuario_actual.rechazados)
            ]
            
            # Mezclar aleatoriamente
            import random
            random.shuffle(libros_respaldo)
            
            return libros_respaldo
    
    def obtener_recomendaciones(self):
        """Obtiene recomendaciones usando el algoritmo de Dijkstra inteligente"""
        try:
            if not self.usuario_actual:
                return []
            
            print(f"🔍 Generando recomendaciones para {self.usuario_actual.id}...")
            
            # Usar algoritmo de Dijkstra
            recomendaciones = recomendar_con_dijkstra(self.usuario_actual.id)
            
            # Guardar en historial
            import datetime
            self.historial_recomendaciones.append({
                'usuario': self.usuario_actual.id,
                'timestamp': datetime.datetime.now(),
                'cantidad': len(recomendaciones),
                'libros': [r.id for r in recomendaciones]
            })
            
            return recomendaciones
            
        except Exception as e:
            print(f"Error al obtener recomendaciones con Dijkstra: {e}")
            return []
    
    def obtener_estadisticas_usuario(self):
        """Obtiene estadísticas del usuario actual"""
        if not self.usuario_actual:
            return {}
        
        total_evaluados = len(self.usuario_actual.aceptados) + len(self.usuario_actual.rechazados)
        
        return {
            'libros_aceptados': len(self.usuario_actual.aceptados),
            'libros_rechazados': len(self.usuario_actual.rechazados),
            'total_evaluados': total_evaluados,
            'preferencia_ritmo': 'rápido' if self.usuario_actual.ritmo['rápido'] > self.usuario_actual.ritmo['lento'] else 'lento',
            'preferencia_final': 'feliz' if self.usuario_actual.finales['feliz'] > self.usuario_actual.finales['trágico'] else 'trágico',
            'elementos_favoritos': self.usuario_actual.elementos,
            'generos_favoritos': getattr(self.usuario_actual, 'generos', []),
            'recomendaciones_generadas': len(self.historial_recomendaciones),
            'porcentaje_aceptacion': round((len(self.usuario_actual.aceptados) / max(1, total_evaluados)) * 100, 1)
        }
    
    def obtener_libro_por_id(self, libro_id):
        """Obtiene un libro específico por su ID"""
        return next((libro for libro in self.libros_sistema if libro.id == libro_id), None)
    
    def reiniciar_preferencias_usuario(self):
        """Reinicia las preferencias del usuario a valores predeterminados"""
        if not self.usuario_actual:
            return False
        
        # Resetear preferencias
        self.usuario_actual.ritmo = {"rápido": 0.5, "lento": 0.5}
        self.usuario_actual.finales = {"feliz": 0.5, "trágico": 0.5}
        self.usuario_actual.elementos = []
        
        # Limpiar cache
        self.cache_evaluaciones = {}
        
        return True
    
    def exportar_datos_usuario(self):
        """Exporta los datos del usuario actual para análisis"""
        if not self.usuario_actual:
            return None
        
        return {
            'usuario_id': self.usuario_actual.id,
            'preferencias': {
                'ritmo': self.usuario_actual.ritmo,
                'finales': self.usuario_actual.finales,
                'elementos': self.usuario_actual.elementos
            },
            'evaluaciones': {
                'aceptados': self.usuario_actual.aceptados,
                'rechazados': self.usuario_actual.rechazados
            },
            'generos': getattr(self.usuario_actual, 'generos', []),
            'estadisticas': self.obtener_estadisticas_usuario(),
            'historial_recomendaciones': self.historial_recomendaciones
        }
    
    def cerrar_sesion(self):
        """Cierra la sesión del usuario actual y limpia recursos de Dijkstra"""
        try:
            limpiar_grafo_proyectado()
        except:
            pass
        
        # Limpiar datos de sesión
        self.usuario_actual = None
        self.historial_recomendaciones = []
        self.cache_evaluaciones = {}
        
        print("👋 Sesión cerrada correctamente")
    
    def usuario_autenticado(self):
        """Verifica si hay un usuario autenticado"""
        return self.usuario_actual is not None
    
    def obtener_info_sistema(self):
        """Obtiene información general del sistema"""
        return {
            'total_libros': len(self.libros_sistema),
            'usuario_actual': self.usuario_actual.id if self.usuario_actual else None,
            'cache_activo': len(self.cache_evaluaciones) > 0,
            'historial_sesion': len(self.historial_recomendaciones)
        }