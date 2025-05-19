def actualizar_perfil(usuario, libro, accion):
    if accion == "aceptar":
        usuario.ritmo[libro.ritmo] = usuario.ritmo.get(libro.ritmo, 0) + 0.1
        usuario.finales[libro.final] = usuario.finales.get(libro.final, 0) + 0.1
        for e in libro.elementos:
            if e not in usuario.elementos:
                usuario.elementos.append(e)
        usuario.aceptados.append(libro.id)

    elif accion == "rechazar":
        usuario.ritmo[libro.ritmo] = usuario.ritmo.get(libro.ritmo, 0) - 0.15
        usuario.rechazados.append(libro.id)

