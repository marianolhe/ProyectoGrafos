class Usuario:
    def __init__(self, id, ritmo, finales, elementos, aceptados=None, rechazados=None):
        self.id = id
        self.ritmo = ritmo
        self.finales = finales
        self.elementos = elementos
        self.aceptados = aceptados or []
        self.rechazados = rechazados or []
