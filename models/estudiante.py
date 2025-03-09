class Estudiante:
    """Clase que representa a un estudiante en el sistema."""
    
    def __init__(self, id_estudiante, nombre, cuatrimestre, status, creditos_acumulados, max_creditos):
        """Inicializa un nuevo estudiante.
        
        Args:
            id_estudiante (int): Identificador único del estudiante.
            nombre (str): Nombre completo del estudiante.
            cuatrimestre (int): Cuatrimestre actual del estudiante.
            status (str): Status del estudiante (Regular o Irregular).
            creditos_acumulados (float): Créditos acumulados por el estudiante.
            max_creditos (float): Créditos máximos que puede cursar por cuatrimestre.
        """
        self.id = id_estudiante
        self.nombre = nombre
        self.cuatrimestre = cuatrimestre
        self.status = status
        self.creditos_acumulados = creditos_acumulados
        self.max_creditos = max_creditos
        self.materias_aprobadas = set()  # Conjunto de IDs de materias aprobadas
        self.preferencias = {}  # Diccionario de preferencias
    
    def agregar_materia_aprobada(self, id_materia):
        """Agrega una materia aprobada al historial del estudiante."""
        self.materias_aprobadas.add(id_materia)
    
    
    def establecer_preferencias(self, preferencias):
        """Establece las preferencias del estudiante."""
        self.preferencias = preferencias
    
    def es_regular(self):
        """Verifica si el estudiante es regular.
        
        Un estudiante es regular si su status está marcado como 'Regular', 
        lo que indica que debe seguir estrictamente el plan de estudios.
        
        Returns:
            bool: True si el estudiante es regular, False si es irregular.
        """
        return self.status.lower() == 'regular'
    
    def to_dict(self):
        """Convierte el estudiante a un diccionario."""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'cuatrimestre': self.cuatrimestre,
            'status': self.status,
            'creditos_acumulados': self.creditos_acumulados,
            'max_creditos': self.max_creditos,
            'materias_aprobadas': list(self.materias_aprobadas),
            'preferencias': self.preferencias
        }
    
    def __str__(self):
        return f"{self.nombre} (ID: {self.id}, Cuatrimestre: {self.cuatrimestre}, Status: {self.status})"