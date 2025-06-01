class InterfazUsuario:
    def __init__(self):
        pass
    
    def mostrar_menu_principal(self):
        """Muestra el menú principal del sistema"""
        print("\n" + "="*60)
        print("    SISTEMA DE RECOMENDACIÓN DE LIBROS")
        print("         (Algoritmo de Dijkstra)")
        print("="*60)
        print("1. Iniciar sesión")
        print("2. Registrarse")
        print("3. Salir")
        print("="*60)
        return input("Seleccione una opción: ").strip()
    
    def solicitar_datos_registro(self):
        """Solicita los datos necesarios para registrar un nuevo usuario"""
        print("\n" + "="*40)
        print("         REGISTRO DE USUARIO")
        print("="*40)
        
        usuario_id = input("Crea un ID de usuario: ").strip()
        password = input("Crea una contraseña: ").strip()
        
        print(f"\nCreando nuevo usuario {usuario_id}...")
        print("Responde el siguiente cuestionario para configurar tus preferencias.\n")
        
        # Géneros favoritos
        print("Selecciona tus 3 géneros favoritos (separados por coma):")
        print("Opciones: Thriller, Fantasía, Ciencia Ficción, Romance, Histórico, Misterio")
        generos_input = input("Géneros: ").strip()
        generos = [g.strip().capitalize() for g in generos_input.split(',')[:3]]
        
        # Preferencia de ritmo
        print("\n¿Prefieres historias con ritmo rápido y dinámico o lento y detallado?")
        ritmo_op = input("(rápido/lento/ninguno): ").strip().lower()
        
        # Tipo de finales
        print("\n¿Qué tipo de finales prefieres?")
        print("Opciones: sorprendentes, felices, trágicos, abiertos")
        final_op = input("Final: ").strip().lower()
        
        # Elementos narrativos
        print("\n¿Qué elementos te enganchan más en una historia? (elige hasta 2 separados por coma)")
        print("Opciones: giros, personajes, mundos, romance, acción")
        elementos_input = input("Elementos: ").strip().lower()
        elementos = [e.strip() for e in elementos_input.split(',')[:2]]
        
        return usuario_id, password, generos, ritmo_op, final_op, elementos
    
    def solicitar_datos_login(self):
        """Solicita las credenciales para iniciar sesión"""
        print("\n" + "="*40)
        print("         INICIAR SESIÓN")
        print("="*40)
        
        usuario_id = input("Ingresa tu ID de usuario: ").strip()
        password = input("Ingresa tu contraseña: ").strip()
        
        return usuario_id, password
    
    def mostrar_libro_para_evaluacion(self, libro):
        """Muestra la información de un libro para que el usuario lo evalúe"""
        print("\n" + "-"*40)
        print(f"Libro: {libro.id}")
        print(f"Ritmo: {libro.ritmo}")
        print(f"Final: {libro.final}")
        print(f"Elementos: {', '.join(libro.elementos)}")
        print(f"Puntuación global: {libro.puntuacion_global}")
        print("-"*40)
        
        while True:
            respuesta = input("¿Quieres aceptar (A) o rechazar (R) este libro? ").strip().lower()
            if respuesta in ["a", "r"]:
                return respuesta == "a"
            print("Por favor, responde 'A' para aceptar o 'R' para rechazar.")
    
    def mostrar_recomendaciones(self, recomendaciones):
        """Muestra las recomendaciones generadas por Dijkstra"""
        print("\n" + "="*60)
        print("    RECOMENDACIONES PERSONALIZADAS")
        print("        (Generadas con Algoritmo de Dijkstra)")
        print("="*60)
        
        if recomendaciones:
            print("Basado en las rutas más cortas en la red de preferencias:")
            for i, libro in enumerate(recomendaciones, 1):
                print(f"\n{i}. Libro: {libro.id}")
                print(f"   Puntaje: {libro.puntaje:.2f}")
                print(f"   Motivo: {libro.motivo}")
                if hasattr(libro, 'ritmo'):
                    print(f"   Características: Ritmo {libro.ritmo}, Final {libro.final}")
                    print(f"   Elementos: {', '.join(libro.elementos)}")
                    print(f"   Puntuación global: {libro.puntuacion_global}")
        else:
            print("No se encontraron recomendaciones en este momento.")
            print("Intenta evaluar más libros para mejorar la red de preferencias.")
    
    def mostrar_mensaje(self, mensaje):
        """Muestra un mensaje al usuario"""
        print(f"\n{mensaje}")
    
    def mostrar_error(self, error):
        """Muestra un mensaje de error al usuario"""
        print(f"\n❌ Error: {error}")
    
    def mostrar_exito(self, mensaje):
        """Muestra un mensaje de éxito al usuario"""
        print(f"\n✅ {mensaje}")
    
    def confirmar_salida(self):
        """Solicita confirmación para salir del programa"""
        print("\n¡Gracias por usar nuestro sistema de recomendaciones!")
        print("El algoritmo de Dijkstra ha optimizado tus preferencias.")
        print("¡Hasta pronto!")
    
    def mostrar_no_hay_libros(self):
        """Muestra mensaje cuando no hay más libros para evaluar"""
        print("\n" + "="*50)
        print("No hay más libros disponibles para evaluar.")
        print("Generando recomendaciones con Dijkstra...")
        print("="*50)
    
    def pausar(self):
        """Pausa la ejecución para que el usuario pueda leer"""
        input("\nPresiona Enter para continuar...")
    
    def mostrar_procesando_dijkstra(self):
        """Muestra mensaje mientras se procesa Dijkstra"""
        print("\n🔄 Calculando rutas óptimas con algoritmo de Dijkstra...")
        print("   Analizando la red de preferencias y similitudes...")