from Sistema_Recomendacion import SistemaRecomendacion
from Interfaz_Usuario import InterfazUsuario

def main():
    """Función principal del programa"""
    # Inicializar sistema e interfaz
    sistema = SistemaRecomendacion()
    interfaz = InterfazUsuario()
    
    # Mostrar mensaje de bienvenida
    print("\n🎯 Sistema de Recomendación de Libros")
    print("💡 Utilizando algoritmo de Dijkstra para encontrar las mejores rutas")
    print("   hacia tus próximas lecturas favoritas")
    
    # Bucle principal del programa
    while True:
        opcion = interfaz.mostrar_menu_principal()
        
        if opcion == "1":
            manejar_inicio_sesion(sistema, interfaz)
        elif opcion == "2":
            manejar_registro(sistema, interfaz)
        elif opcion == "3":
            interfaz.confirmar_salida()
            break
        else:
            interfaz.mostrar_error("Opción no válida. Por favor, intente de nuevo.")
        
        # Si el usuario está autenticado, continuar con el flujo principal
        if sistema.usuario_autenticado():
            ejecutar_flujo_principal(sistema, interfaz)
            sistema.cerrar_sesion()

def manejar_registro(sistema, interfaz):
    """Maneja el proceso de registro de usuario"""
    try:
        # Solicitar datos de registro
        usuario_id, password, generos, ritmo_op, final_op, elementos = interfaz.solicitar_datos_registro()
        
        # Intentar registrar usuario
        exito, mensaje = sistema.registrar_nuevo_usuario(
            usuario_id, password, generos, ritmo_op, final_op, elementos
        )
        
        if exito:
            interfaz.mostrar_exito(mensaje)
            interfaz.mostrar_mensaje("✨ Tu perfil se ha integrado en la red de Dijkstra")
        else:
            interfaz.mostrar_error(mensaje)
            
    except KeyboardInterrupt:
        interfaz.mostrar_mensaje("Registro cancelado por el usuario.")
    except Exception as e:
        interfaz.mostrar_error(f"Error inesperado durante el registro: {e}")

def manejar_inicio_sesion(sistema, interfaz):
    """Maneja el proceso de inicio de sesión"""
    try:
        # Solicitar credenciales
        usuario_id, password = interfaz.solicitar_datos_login()
        
        # Intentar autenticar
        exito, mensaje = sistema.autenticar_usuario(usuario_id, password)
        
        if exito:
            interfaz.mostrar_exito(mensaje)
            interfaz.mostrar_mensaje("🔗 Conectándose a la red de preferencias...")
        else:
            interfaz.mostrar_error(mensaje)
            
    except KeyboardInterrupt:
        interfaz.mostrar_mensaje("Inicio de sesión cancelado por el usuario.")
    except Exception as e:
        interfaz.mostrar_error(f"Error inesperado durante el inicio de sesión: {e}")

def ejecutar_flujo_principal(sistema, interfaz):
    """Ejecuta el flujo principal del programa una vez autenticado el usuario"""
    try:
        # Obtener libros para evaluar
        libros_para_evaluar = sistema.obtener_libros_para_evaluar()
        
        if libros_para_evaluar:
            interfaz.mostrar_mensaje("📚 Evalúa estos libros para mejorar las recomendaciones de Dijkstra:")
            
            # Evaluar libros
            for libro in libros_para_evaluar:
                try:
                    acepta = interfaz.mostrar_libro_para_evaluacion(libro)
                    exito, mensaje = sistema.evaluar_libro(libro.id, acepta)
                    
                    if exito:
                        accion = "aceptado" if acepta else "rechazado"
                        interfaz.mostrar_exito(f"Has {accion} el libro {libro.id}")
                        interfaz.mostrar_mensaje("🔄 Actualizando red de preferencias...")
                    else:
                        interfaz.mostrar_error(mensaje)
                        
                except KeyboardInterrupt:
                    interfaz.mostrar_mensaje("Evaluación cancelada por el usuario.")
                    break
                    
        else:
            interfaz.mostrar_no_hay_libros()
        
        # Mostrar que se está procesando con Dijkstra
        interfaz.mostrar_procesando_dijkstra()
        
        # Generar y mostrar recomendaciones usando únicamente Dijkstra
        recomendaciones = sistema.obtener_recomendaciones()
        interfaz.mostrar_recomendaciones(recomendaciones)
        
        # Pausa para que el usuario pueda leer las recomendaciones
        interfaz.pausar()
        
    except Exception as e:
        interfaz.mostrar_error(f"Error durante la ejecución principal: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🚪 Programa interrumpido por el usuario.")
        print("Limpiando recursos de Dijkstra... ¡Hasta pronto!")
    except Exception as e:
        print(f"\n💥 Error crítico: {e}")
        print("El programa se cerrará.")