class Horario:
    """Clase que representa un horario académico."""
    
    DIAS = {
        1: "Lunes",
        2: "Martes",
        3: "Miércoles",
        4: "Jueves",
        5: "Viernes"
    }
    
    def __init__(self, grupos=None):
        """Inicializa un nuevo horario.
        
        Args:
            grupos (list, optional): Lista de IDs de grupos que conforman el horario.
        """
        self.grupos = grupos or []
        self.horario_semanal = self._inicializar_horario_semanal()
    
    def _inicializar_horario_semanal(self):
        """Inicializa la estructura del horario semanal."""
        horario = {}
        for dia in self.DIAS.keys():
            horario[dia] = {}
            for hora in range(7, 22):  # De 7am a 9pm
                horario[dia][hora] = None
        return horario
    
    def agregar_grupo(self, id_grupo, grupo_obj, materia_obj):
        """Agrega un grupo al horario.
        
        Args:
            id_grupo (int): ID del grupo a agregar.
            grupo_obj (Grupo): Objeto Grupo correspondiente.
            materia_obj (Materia): Objeto Materia correspondiente.
            
        Returns:
            bool: True si se pudo agregar, False si hay conflicto.
        """
        # Verificar conflictos con otros grupos ya asignados
        for horario in grupo_obj.horarios:
            dia, hora_inicio, hora_fin, _ = horario
            
            # Convertir horas a enteros si vienen como strings
            if isinstance(hora_inicio, str):
                hora_inicio = int(hora_inicio.split(':')[0])
            if isinstance(hora_fin, str):
                hora_fin = int(hora_fin.split(':')[0])
            
            # Verificar conflictos
            for hora in range(hora_inicio, hora_fin):
                if self.horario_semanal[dia][hora] is not None:
                    return False
        
        # Si no hay conflictos, agregar el grupo
        self.grupos.append(id_grupo)
        
        # Actualizar horario semanal
        for horario in grupo_obj.horarios:
            dia, hora_inicio, hora_fin, aula = horario
            
            # Convertir horas a enteros si vienen como strings
            if isinstance(hora_inicio, str):
                hora_inicio = int(hora_inicio.split(':')[0])
            if isinstance(hora_fin, str):
                hora_fin = int(hora_fin.split(':')[0])
            
            # Agregar información de la clase al horario
            for hora in range(hora_inicio, hora_fin):
                self.horario_semanal[dia][hora] = {
                    'id_grupo': id_grupo,
                    'materia': materia_obj.nombre,
                    'profesor': grupo_obj.profesor,
                    'aula': aula
                }
        
        return True
    
    def obtener_materias(self, grupos_dict, materias_dict):
        """Obtiene la lista de materias en el horario.
        
        Args:
            grupos_dict (dict): Diccionario de objetos Grupo por ID.
            materias_dict (dict): Diccionario de objetos Materia por ID.
            
        Returns:
            list: Lista de diccionarios con información de las materias.
        """
        materias = []
        materias_ids = set()
        
        for id_grupo in self.grupos:
            grupo = grupos_dict.get(id_grupo)
            if grupo:
                id_materia = grupo.id_materia
                if id_materia not in materias_ids:
                    materia = materias_dict.get(id_materia)
                    if materia:
                        materias_ids.add(id_materia)
                        materias.append({
                            'id': id_materia,
                            'nombre': materia.nombre,
                            'creditos': materia.creditos,
                            'cuatrimestre': materia.cuatrimestre,
                            'tipo': materia.tipo,
                            'grupos': []
                        })
                
                # Agregar grupo a la materia correspondiente
                for materia in materias:
                    if materia['id'] == id_materia:
                        materia['grupos'].append({
                            'id': id_grupo,
                            'profesor': grupo.profesor,
                            'horarios': grupo.horarios
                        })
        
        return materias
    
    def calcular_estadisticas(self, grupos_dict, materias_dict):
        """Calcula estadísticas del horario.
        
        Args:
            grupos_dict (dict): Diccionario de objetos Grupo por ID.
            materias_dict (dict): Diccionario de objetos Materia por ID.
            
        Returns:
            dict: Diccionario con estadísticas del horario.
        """
        # Contar materias y créditos
        materias_unicas = set()
        total_creditos = 0
        
        for id_grupo in self.grupos:
            grupo = grupos_dict.get(id_grupo)
            if grupo:
                id_materia = grupo.id_materia
                materia = materias_dict.get(id_materia)
                if materia and id_materia not in materias_unicas:
                    materias_unicas.add(id_materia)
                    total_creditos += materia.creditos
        
        # Calcular carga por día
        carga_por_dia = {dia: 0 for dia in self.DIAS.keys()}
        for dia, horas in self.horario_semanal.items():
            materias_en_dia = set()
            for hora, info in horas.items():
                if info is not None:
                    id_grupo = info['id_grupo']
                    grupo = grupos_dict.get(id_grupo)
                    if grupo:
                        materias_en_dia.add(grupo.id_materia)
            carga_por_dia[dia] = len(materias_en_dia)
        
        # Calcular horas por día
        horas_por_dia = {dia: 0 for dia in self.DIAS.keys()}
        for dia, horas in self.horario_semanal.items():
            for hora, info in horas.items():
                if info is not None:
                    horas_por_dia[dia] += 1
        
        return {
            'total_materias': len(materias_unicas),
            'total_creditos': total_creditos,
            'carga_por_dia': carga_por_dia,
            'horas_por_dia': horas_por_dia
        }
    
    def to_dict(self):
        """Convierte el horario a un diccionario."""
        horario_formateado = {}
        
        for dia, horas in self.horario_semanal.items():
            dia_nombre = self.DIAS.get(dia, f"Día {dia}")
            horario_formateado[dia_nombre] = {}
            
            for hora, info in horas.items():
                hora_str = f"{hora}:00"
                if info is not None:
                    horario_formateado[dia_nombre][hora_str] = {
                        'materia': info['materia'],
                        'profesor': info['profesor'],
                        'aula': info['aula'],
                        'id_grupo': info['id_grupo']
                    }
                else:
                    horario_formateado[dia_nombre][hora_str] = None
        
        return {
            'grupos': self.grupos,
            'horario_semanal': horario_formateado
        }