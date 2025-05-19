from Usuario import Usuario
from Libro import Libro
from Recomendador import recomendar_libros
from Datos import crear_usuario, crear_libro, crear_interaccion, autenticar_usuario, verificar_usuario_existente, crear_genero, crear_relacion_prefiere, crear_relacion_posee, obtener_datos_usuario

def mostrar_menu():
    print("\n===== SISTEMA DE RECOMENDACIÓN DE LIBROS =====")
    print("1. Iniciar sesión")
    print("2. Registrarse")
    print("3. Salir")
    return input("Seleccione una opción: ")

def crear_nuevo_usuario():
    usuario_valido = False
    while not usuario_valido:
        usuario_id = input("Crea un ID de usuario: ")
        usuario_valido = not verificar_usuario_existente(usuario_id)
        if not usuario_valido:
            print("Este ID de usuario ya existe. Por favor, elige otro.")
    
    password = input("Crea una contraseña: ")
    print(f"\nCreando nuevo usuario {usuario_id}...\nResponde el siguiente cuestionario para configurar tus preferencias.")
    
    # Cuestionario obligatorio para nuevos usuarios
    print("Selecciona tus 3 géneros favoritos (separados por coma):")
    print("Opciones: Thriller, Fantasía, Ciencia Ficción, Romance, Histórico, Misterio")
    generos = input("Géneros: ").split(',')
    generos = [g.strip().capitalize() for g in generos[:3]]

    print("\n¿Prefieres historias con ritmo rápido y dinámico o lento y detallado?")
    ritmo_op = input("(rápido/lento/ninguno): ").strip().lower()
    ritmo = {"rápido": 1.0 if ritmo_op == "rápido" else 0.0,
            "lento": 1.0 if ritmo_op == "lento" else 0.0}

    print("\n¿Qué tipo de finales prefieres?")
    print("Opciones: sorprendentes, felices, trágicos, abiertos")
    final_op = input("Final: ").strip().lower()
    finales = {"feliz": 1.0 if final_op == "felices" else 0.0,
            "trágico": 1.0 if final_op == "trágicos" else 0.0}

    print("\n¿Qué elementos te enganchan más en una historia? (elige hasta 2 separados por coma)")
    print("Opciones: giros, personajes, mundos, romance, acción")
    elementos = input("Elementos: ").strip().lower().split(',')
    elementos = [e.strip() for e in elementos[:2]]

    usuario = Usuario(
        id=usuario_id,
        password=password,
        ritmo=ritmo,
        finales=finales,
        elementos=elementos
    )
    crear_usuario(usuario)
    for g in generos:
        crear_genero(g)
        crear_relacion_prefiere(usuario_id, g)
        
    print(f"¡Usuario {usuario_id} creado exitosamente!")
    return usuario

def iniciar_sesion():
    usuario_id = input("Ingresa tu ID de usuario: ")
    password = input("Ingresa tu contraseña: ")
    
    if autenticar_usuario(usuario_id, password):
        print(f"Bienvenido de nuevo, {usuario_id}!")
        
        # Agregar función para cargar preferencias del usuario desde la base de datos
        datos_usuario = obtener_datos_usuario(usuario_id)
        
        usuario = Usuario(
            id=usuario_id,
            password=password,
            ritmo=datos_usuario.get("ritmo", {"rápido": 0.0, "lento": 0.0}),
            finales=datos_usuario.get("finales", {"feliz": 0.0, "trágico": 0.0}),
            elementos=datos_usuario.get("elementos", []),
            aceptados=datos_usuario.get("aceptados", []),
            rechazados=datos_usuario.get("rechazados", [])
        )
        return usuario
    else:
        print("ID de usuario o contraseña incorrectos.")
        return None

# Programa principal
menu_activo = True
usuario = None

while menu_activo and usuario is None:
    opcion = mostrar_menu()
    
    if opcion == "1":
        usuario = iniciar_sesion()
    elif opcion == "2":
        usuario = crear_nuevo_usuario()
    elif opcion == "3":
        print("Gracias por usar nuestro sistema. ¡Hasta pronto!")
        menu_activo = False
    else:
        print("Opción no válida. Por favor, intente de nuevo.")

# Si el usuario ha salido del menú sin iniciar sesión, terminamos el programa
if usuario is None:
    exit()

# Continuar con el resto del programa una vez que el usuario ha iniciado sesión
libro1 = Libro("L1", "rápido", "feliz", ["giros"], 4.7)
libro2 = Libro("L2", "lento", "trágico", ["personajes"], 4.2)

crear_libro(libro1)
crear_libro(libro2)
crear_relacion_posee("L1")
crear_relacion_posee("L2")
crear_interaccion(usuario.id, "L1", "ACEPTO")
crear_interaccion(usuario.id, "L2", "RECHAZO")

libros = [libro1, libro2]
recomendaciones = recomendar_libros(usuario, libros)

for libro in recomendaciones:
    print(f"Libro recomendado: {libro.id} | Puntaje: {libro.puntaje:.2f} | Motivo: Coincide en {libro.motivo}")