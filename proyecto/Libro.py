class Libro:
    def __init__(self, id, ritmo, final, elementos, puntuacion_global, titulo=None):
        self.id = id
        self.titulo = titulo or f"Libro {id}"
        self.ritmo = ritmo
        self.final = final
        self.elementos = elementos if elementos is not None else []
        self.puntuacion_global = puntuacion_global if puntuacion_global is not None else 0.0
        
        # Atributos para recomendaciones (se asignan dinámicamente)
        self.puntaje = 0.0
        self.motivo = ""
        self.usuarios_recomiendan = 0
        
    def __str__(self):
        return f"{self.titulo} ({self.id})"
    
    def __repr__(self):
        return f"Libro(id='{self.id}', titulo='{self.titulo}', puntaje={self.puntaje})"
    
    def obtener_info_completa(self):
        """Retorna información completa del libro para debugging"""
        return {
            'id': self.id,
            'titulo': self.titulo,
            'ritmo': self.ritmo,
            'final': self.final,
            'elementos': self.elementos,
            'puntuacion_global': self.puntuacion_global,
            'puntaje_recomendacion': self.puntaje,
            'motivo': self.motivo
        }