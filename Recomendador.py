from engine.calculo_match import calcular_match
from engine.reglas_adicionales import aplicar_reglas

def recomendar_libros(usuario, libros):
    candidatos = [libro for libro in libros if libro.id not in usuario.aceptados + usuario.rechazados]

    for libro in candidatos:
        libro.puntaje = calcular_match(usuario, libro)

    candidatos.sort(key=lambda l: l.puntaje, reverse=True)
    recomendaciones = aplicar_reglas(usuario, candidatos)
    return recomendaciones[:5]

