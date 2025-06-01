class Libro:
    def __init__(self, id, ritmo, final, elementos, puntuacion_global, titulo=None):
        self.id = id
        self.titulo = titulo or f"Libro {id}"  # Título por defecto si no se proporciona
        self.ritmo = ritmo
        self.final = final
        self.elementos = elementos
        self.puntuacion_global = puntuacion_global
        
    def __str__(self):
        return f"{self.titulo} ({self.id})"