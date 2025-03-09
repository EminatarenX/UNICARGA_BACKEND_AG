class Grupo:
    """Clase que representa un grupo para una materia."""
    
    def __init__(self, id_grupo, id_materia, profesor, cupo_maximo, cupo_actual):
        """Inicializa un nuevo grupo.
        
        Args:
            id_grupo (int): Identificador único del grupo.
            id_materia (int): Identificador de la materia a la que pertenece.
            profesor (str): Nombre del profesor que imparte el grupo.
            cupo_maximo (int): Cupo máximo del grupo.
            cupo_actual (int): Cupo actual del grupo (estudiantes ya inscritos).
        """
        self.id = id_grupo
        self.id_materia = id_materia
        self.profesor = profesor
        self.cupo_maximo = cupo_maximo
        self.cupo_actual = cupo_actual
        self.horarios = []  # Lista de tuplas (día, hora_inicio, hora_fin, aula)
    
    def tiene_cupo(self):
        """Verifica si el grupo tiene cupo disponible.
        
        Considerando el contexto universitario, se permite una pequeña
        flexibilidad en el cupo para representar posibles cargas manuales.
        """
        # Se considera que hay cupo si el actual está a menos del 110% del máximo
        # (para permitir algunas cargas manuales adicionales)
        return self.cupo_actual < (self.cupo_maximo * 1.1)
    
    def agregar_horario(self, dia, hora_inicio, hora_fin, aula):
        """Agrega un horario al grupo."""
        self.horarios.append((dia, hora_inicio, hora_fin, aula))
    
    def to_dict(self):
        """Convierte el grupo a un diccionario."""
        return {
            'id': self.id,
            'id_materia': self.id_materia,
            'profesor': self.profesor,
            'cupo_maximo': self.cupo_maximo,
            'cupo_actual': self.cupo_actual,
            'horarios': self.horarios
        }
    
    def __str__(self):
        return f"Grupo {self.id} (Materia: {self.id_materia}, Profesor: {self.profesor})"