from Usuario import Usuario
from Libro import Libro
from Recomendador import recomendar_libros
from Datos import crear_usuario, crear_libro, crear_interaccion

usuario = Usuario(
    id="u1",
    ritmo={"rápido": 0.8, "lento": 0.2},
    finales={"feliz": 0.6, "trágico": 0.4},
    elementos=["giros", "personajes"]
)

libro1 = Libro("L1", "rápido", "feliz", ["giros"], 4.7)
libro2 = Libro("L2", "lento", "trágico", ["personajes"], 4.2)

crear_usuario(usuario)
crear_libro(libro1)
crear_libro(libro2)

crear_interaccion("u1", "L1", "ACEPTO")
crear_interaccion("u1", "L2", "RECHAZO")

libros = [libro1, libro2]
recomendaciones = recomendar_libros(usuario, libros)

for libro in recomendaciones:
    print(f"Libro recomendado: {libro.id} | Puntaje: {libro.puntaje:.2f}")