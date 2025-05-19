from Usuario import Usuario
from Libro import Libro
from Recomendador import recomendar_libros
from Datos import crear_usuario, crear_libro, crear_interaccion, autenticar_usuario, verificar_usuario_existente, crear_genero, crear_relacion_prefiere, crear_relacion_posee

usuario_id = input("Ingresa tu ID de usuario: ")
password = input("Ingresa tu contraseña: ")

if autenticar_usuario(usuario_id, password):
    print(f"Bienvenido de nuevo, {usuario_id}!")
    usuario = Usuario(
        id=usuario_id,
        password=password,
        ritmo={"rápido": 0.8, "lento": 0.2},
        finales={"feliz": 0.6, "trágico": 0.4},
        elementos=["giros", "personajes"]
    )
else:
    print(f"Creando nuevo usuario {usuario_id}...\nResponde el siguiente cuestionario para configurar tus preferencias.")
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