def calcular_match(usuario, libro):
    score = 0.0
    motivos = []

    if libro.ritmo in usuario.ritmo:
        score += usuario.ritmo[libro.ritmo] * 0.4
        if usuario.ritmo[libro.ritmo] > 0:
            motivos.append(f"ritmo {libro.ritmo}")

    if libro.final in usuario.finales:
        score += usuario.finales[libro.final] * 0.3
        if usuario.finales[libro.final] > 0:
            motivos.append(f"final {libro.final}")

    elementos_comunes = []
    for e in libro.elementos:
        if e in usuario.elementos:
            score += 0.3 / len(usuario.elementos)
            elementos_comunes.append(e)
    
    if elementos_comunes:
        motivos.append("elementos: " + ", ".join(elementos_comunes))

    score += libro.puntuacion_global * 0.05
    
    # Asignar el motivo al libro
    libro.motivo = ", ".join(motivos) if motivos else "puntuación global"

    return score