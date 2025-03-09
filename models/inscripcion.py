class Inscripcion:
    """Clase que representa una inscripción de un estudiante a un grupo."""
    
    def __init__(self, id_inscripcion, id_estudiante, id_grupo, cuatrimestre, 
                 fecha_inscripcion=None, activa=True):
        """Inicializa una nueva inscripción.
        
        Args:
            id_inscripcion (int): Identificador único de la inscripción.
            id_estudiante (int): Identificador del estudiante.
            id_grupo (int): Identificador del grupo.
            cuatrimestre (int): Cuatrimestre en el que se realiza la inscripción.
            fecha_inscripcion (str, optional): Fecha de inscripción en formato 'YYYY-MM-DD'.
            activa (bool, optional): Indica si la inscripción está activa.
        """
        self.id = id_inscripcion
        self.id_estudiante = id_estudiante
        self.id_grupo = id_grupo
        self.cuatrimestre = cuatrimestre
        self.fecha_inscripcion = fecha_inscripcion
        self.activa = activa
    
    def to_dict(self):
        """Convierte la inscripción a un diccionario."""
        return {
            'id': self.id,
            'id_estudiante': self.id_estudiante,
            'id_grupo': self.id_grupo,
            'cuatrimestre': self.cuatrimestre,
            'fecha_inscripcion': self.fecha_inscripcion,
            'activa': self.activa
        }
    
    def __str__(self):
        return f"Inscripción {self.id}: Estudiante {self.id_estudiante} - Grupo {self.id_grupo}"