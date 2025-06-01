from Usuario import Usuario
from Libro import Libro
from Dijkstra_Recomendador import recomendar_con_dijkstra, limpiar_grafo_proyectado
from Datos import crear_usuario, verificar_y_crear_interaccion, autenticar_usuario, verificar_usuario_existente, crear_genero, crear_relacion_prefiere, obtener_datos_usuario

class SistemaRecomendacion:
    def __init__(self):
        self.usuario_actual = None
        self.libros_sistema = []
        self._inicializar_libros_predeterminados()
    
    def _inicializar_libros_predeterminados(self):
        """Carga libros existentes desde la base de datos"""
        try:
            from Datos import conn
            query = "MATCH (l:Libro) RETURN l.id, l.ritmo, l.final, l.elementos, l.puntuacion_global ORDER BY l.id"
            result = conn.run_query(query)
            
            self.libros_sistema = []
            for record in result:
                libro = Libro(
                    record["l.id"],
                    record["l.ritmo"],
                    record["l.final"], 
                    record["l.elementos"] or [],
                    record["l.puntuacion_global"] or 0.0
                )
                self.libros_sistema.append(libro)
                
            print(f"✅ Cargados {len(self.libros_sistema)} libros desde la base de datos")
            
        except Exception as e:
            print(f"Error cargando libros: {e}")
            # Mantener libros básicos si hay error
            libro1 = Libro("L1", "rápido", "feliz", ["giros"], 4.7)
            libro2 = Libro("L2", "lento", "trágico", ["personajes"], 4.2)
            self.libros_sistema = [libro1, libro2]
    
    def registrar_nuevo_usuario(self, usuario_id, password, generos, ritmo_op, final_op, elementos):
        """Registra un nuevo usuario en el sistema"""
        try:
            # Validar que el usuario no exista
            if verificar_usuario_existente(usuario_id):
                return False, "El ID de usuario ya existe"
            
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
            return True, f"Usuario {usuario_id} creado exitosamente"
            
        except Exception as e:
            return False, f"Error al crear usuario: {e}"
    
    def autenticar_usuario(self, usuario_id, password):
        """Autentica un usuario y carga sus datos"""
        try:
            if autenticar_usuario(usuario_id, password):
                # Obtener datos del usuario
                datos_usuario = obtener_datos_usuario(usuario_id)
                
                if not datos_usuario:
                    # Valores predeterminados si no se pueden recuperar datos
                    datos_usuario = {
                        "ritmo": {"rápido": 0.5, "lento": 0.5},
                        "finales": {"feliz": 0.5, "trágico": 0.5},
                        "elementos": [],
                        "aceptados": [],
                        "rechazados": []
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
                
                return True, f"Bienvenido de nuevo, {usuario_id}!"
            else:
                return False, "ID de usuario o contraseña incorrectos"
                
        except Exception as e:
            return False, f"Error de autenticación: {e}"
    
    def evaluar_libro(self, libro_id, acepta):
        """Registra la evaluación de un libro por parte del usuario"""
        try:
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
                
                return True, f"Evaluación registrada exitosamente"
            else:
                return False, "Error al registrar la evaluación"
                
        except Exception as e:
            return False, f"Error al evaluar libro: {e}"
    
    def obtener_recomendaciones(self):
        """Obtiene recomendaciones usando únicamente el algoritmo de Dijkstra"""
        try:
            if not self.usuario_actual:
                return []
            
            # Usar únicamente Dijkstra
            recomendaciones = recomendar_con_dijkstra(self.usuario_actual.id)
            return recomendaciones
            
        except Exception as e:
            print(f"Error al obtener recomendaciones con Dijkstra: {e}")
            return []
    
    def obtener_libros_para_evaluar(self):
        """Obtiene los libros que el usuario puede evaluar"""
        if not self.usuario_actual:
            return []
        
        # Filtrar libros que el usuario ya evaluó
        libros_no_evaluados = [
            libro for libro in self.libros_sistema 
            if libro.id not in (self.usuario_actual.aceptados + self.usuario_actual.rechazados)
        ]
        
        return libros_no_evaluados
    
    def cerrar_sesion(self):
        """Cierra la sesión del usuario actual y limpia recursos de Dijkstra"""
        try:
            limpiar_grafo_proyectado()
        except:
            pass
        self.usuario_actual = None
    
    def usuario_autenticado(self):
        """Verifica si hay un usuario autenticado"""
        return self.usuario_actual is not None