class Materia:
    """Clase que representa una materia en el plan de estudios."""
    
    def __init__(self, id_materia, nombre, cuatrimestre, creditos, horas_totales, tipo):
        """Inicializa una nueva materia.
        
        Args:
            id_materia (int): Identificador único de la materia.
            nombre (str): Nombre de la materia.
            cuatrimestre (int): Cuatrimestre al que pertenece la materia.
            creditos (float): Créditos que vale la materia.
            horas_totales (int): Horas totales de la materia.
            tipo (str): Tipo de materia (Regular, Proyecto Integrador, Estadía).
        """
        self.id = id_materia
        self.nombre = nombre
        self.cuatrimestre = cuatrimestre
        self.creditos = creditos
        self.horas_totales = horas_totales
        self.tipo = tipo
    
    def to_dict(self):
        """Convierte la materia a un diccionario."""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'cuatrimestre': self.cuatrimestre,
            'creditos': self.creditos,
            'horas_totales': self.horas_totales,
            'tipo': self.tipo
        }
    
    def __str__(self):
        return f"{self.nombre} (ID: {self.id}, Cuatrimestre: {self.cuatrimestre})"