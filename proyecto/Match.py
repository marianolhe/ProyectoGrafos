def calcular_match(usuario, libro):
    score = 0.0

    if libro.ritmo in usuario.ritmo:
        score += usuario.ritmo[libro.ritmo] * 0.4

    if libro.final in usuario.finales:
        score += usuario.finales[libro.final] * 0.3

    for e in libro.elementos:
        if e in usuario.elementos:
            score += 0.3 / len(usuario.elementos)

    score += libro.puntuacion_global * 0.05

    return score
