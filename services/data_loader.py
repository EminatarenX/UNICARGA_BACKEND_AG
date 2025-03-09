import pandas as pd
import os
from models.materia import Materia
from models.grupo import Grupo
from models.estudiante import Estudiante
import random
from models.inscripcion import Inscripcion

class DataLoader:
    """Servicio para cargar datos desde archivos CSV."""
    
    def __init__(self, data_dir="data"):
        """Inicializa el cargador de datos.
        
        Args:
            data_dir: Directorio donde se encuentran los archivos CSV
        """
        self.data_dir = data_dir
        self.materias = {}
        self.grupos = {}
        self.seriacion = {}
        self.dependencias_proyectos = {}
        self.estudiantes = {}
        self.historial_academico = {}
        self.preferencias = {}
        self.horarios = {}
    
    def cargar_todo(self):
        """Carga todos los datos necesarios desde los CSV."""
        self.cargar_materias()
        self.cargar_seriacion()
        self.cargar_dependencias_proyectos()
        self.cargar_grupos()
        self.cargar_horarios()
        self.cargar_estudiantes()
        self.cargar_historial_academico()
        self.cargar_preferencias()
        self.cargar_inscripciones()

    
    def cargar_inscripciones(self):
        """Carga las inscripciones desde inscripciones.csv o las simula si no existe el archivo."""
        ruta = os.path.join(self.data_dir, "inscripciones.csv")
        
        # Inicializar el diccionario de inscripciones
        self.inscripciones = {}
        
        if not os.path.exists(ruta):
            # Si no existe el archivo, crear datos simulados
            return self.simular_inscripciones()
            
        try:
            df = pd.read_csv(ruta)
            
            for _, row in df.iterrows():
                inscripcion = Inscripcion(
                    id_inscripcion=row['id_inscripcion'],
                    id_estudiante=row['id_estudiante'],
                    id_grupo=row['id_grupo'],
                    cuatrimestre=row['cuatrimestre'],
                    fecha_inscripcion=row.get('fecha_inscripcion'),
                    activa=row.get('activa', True)
                )
                
                if inscripcion.id_estudiante not in self.inscripciones:
                    self.inscripciones[inscripcion.id_estudiante] = []
                
                self.inscripciones[inscripcion.id_estudiante].append(inscripcion)
        
        except Exception as e:
            print(f"Error al cargar inscripciones: {e}")
            # Si hay error al cargar, simular inscripciones
            self.simular_inscripciones()

    def verificar_compatibilidad_horaria(self, nuevo_grupo, inscripciones_actuales):
        """
        Verifica si un nuevo grupo es compatible con las inscripciones actuales.
        
        Args:
            nuevo_grupo (Grupo): Grupo que se quiere añadir
            inscripciones_actuales (list): Lista de inscripciones actuales
            
        Returns:
            bool: True si es compatible, False si hay conflicto
        """
        if not hasattr(nuevo_grupo, 'horarios') or not nuevo_grupo.horarios:
            return True  # Si no tiene horario, se considera compatible
        
        for inscripcion in inscripciones_actuales:
            grupo_inscrito = self.grupos.get(inscripcion.id_grupo)
            if not grupo_inscrito or not hasattr(grupo_inscrito, 'horarios') or not grupo_inscrito.horarios:
                continue
                
            for dia_nuevo, inicio_nuevo, fin_nuevo, _ in nuevo_grupo.horarios:
                for dia_inscrito, inicio_inscrito, fin_inscrito, _ in grupo_inscrito.horarios:
                    if dia_nuevo != dia_inscrito:
                        continue
                        
                    # Convertir horas a enteros si son strings
                    if isinstance(inicio_nuevo, str):
                        inicio_nuevo = int(inicio_nuevo.split(':')[0])
                    if isinstance(fin_nuevo, str):
                        fin_nuevo = int(fin_nuevo.split(':')[0])
                    if isinstance(inicio_inscrito, str):
                        inicio_inscrito = int(inicio_inscrito.split(':')[0])
                    if isinstance(fin_inscrito, str):
                        fin_inscrito = int(fin_inscrito.split(':')[0])
                    
                    # Verificar superposición de horarios
                    if (inicio_nuevo <= inicio_inscrito < fin_nuevo or 
                        inicio_nuevo < fin_inscrito <= fin_nuevo or 
                        inicio_inscrito <= inicio_nuevo < fin_inscrito or 
                        inicio_inscrito < fin_nuevo <= fin_inscrito):
                        return False  # Hay conflicto
        
        return True  # No hay conflicto

    def guardar_inscripciones_simuladas(self):
        """Guarda las inscripciones simuladas en un archivo CSV."""
        ruta = os.path.join(self.data_dir, "inscripciones.csv")
        
        inscripciones_lista = []
        for id_estudiante, inscripciones in self.inscripciones.items():
            for inscripcion in inscripciones:
                inscripciones_lista.append({
                    'id_inscripcion': inscripcion.id,
                    'id_estudiante': inscripcion.id_estudiante,
                    'id_grupo': inscripcion.id_grupo,
                    'cuatrimestre': inscripcion.cuatrimestre,
                    'fecha_inscripcion': inscripcion.fecha_inscripcion,
                    'activa': inscripcion.activa
                })
        
        if inscripciones_lista:
            try:
                df = pd.DataFrame(inscripciones_lista)
                df.to_csv(ruta, index=False)
                print(f"Inscripciones simuladas guardadas en {ruta}")
            except Exception as e:
                print(f"Error al guardar inscripciones simuladas: {e}")

    def obtener_grupos_inscritos(self, id_estudiante):
        """
        Obtiene los IDs de grupos en los que un estudiante está inscrito.
        
        Args:
            id_estudiante (int): ID del estudiante
            
        Returns:
            list: Lista de IDs de grupos inscritos
        """
        inscripciones = self.inscripciones.get(id_estudiante, [])
        return [inscripcion.id_grupo for inscripcion in inscripciones if inscripcion.activa]
        
    def obtener_inscripciones(self, id_estudiante):
        """
        Obtiene las inscripciones de un estudiante.
        
        Args:
            id_estudiante (int): ID del estudiante
            
        Returns:
            list: Lista de objetos Inscripcion
        """
        return self.inscripciones.get(id_estudiante, [])

    def simular_inscripciones(self):
        """
        Genera inscripciones simuladas basadas en estudiantes y materias disponibles.
        Esta función se utiliza cuando no existe un archivo de inscripciones real.
        """
        print("Simulando inscripciones para estudiantes...")
        
        # ID único para inscripciones
        id_inscripcion = 1
        
        # Para cada estudiante, simular inscripciones basadas en materias disponibles
        for id_estudiante, estudiante in self.estudiantes.items():
            # Solo consideramos estudiantes en cuatrimestres activos (1-9)
            if not 1 <= estudiante.cuatrimestre <= 9:
                continue
                
            # Obtener materias que el estudiante puede cursar
            materias_disponibles = self.obtener_materias_disponibles(estudiante)
            
            # Determinar cuántas materias inscribir
            # Regulares: 6-7 materias, Irregulares: 3-5 materias
            if estudiante.status == "Regular":
                num_materias = min(len(materias_disponibles), random.randint(6, 7))
            else:
                num_materias = min(len(materias_disponibles), random.randint(3, 5))
            
            # Seleccionar materias priorizando las de cuatrimestres anteriores
            materias_seleccionadas = self.priorizar_materias_para_inscripcion(
                materias_disponibles, estudiante.cuatrimestre, num_materias)
            
            inscripciones_estudiante = []
            
            # Para cada materia seleccionada, buscar un grupo disponible
            for id_materia in materias_seleccionadas:
                # Buscar grupos disponibles para esta materia
                grupos_disponibles = []
                for id_grupo, grupo in self.grupos.items():
                    if (grupo.id_materia == id_materia and 
                        grupo.tiene_cupo() and 
                        self.verificar_compatibilidad_horaria(grupo, inscripciones_estudiante)):
                        grupos_disponibles.append(id_grupo)
                
                # Si hay grupos disponibles, elegir uno al azar
                if grupos_disponibles:
                    id_grupo = random.choice(grupos_disponibles)
                    
                    # Crear inscripción
                    inscripcion = Inscripcion(
                        id_inscripcion=id_inscripcion,
                        id_estudiante=id_estudiante,
                        id_grupo=id_grupo,
                        cuatrimestre=estudiante.cuatrimestre,
                        fecha_inscripcion="2025-02-01",  # Fecha simulada
                        activa=True
                    )
                    
                    inscripciones_estudiante.append(inscripcion)
                    id_inscripcion += 1
                    
                    # Actualizar el cupo del grupo
                    self.grupos[id_grupo].cupo_actual += 1
            
            # Guardar inscripciones del estudiante
            if inscripciones_estudiante:
                self.inscripciones[id_estudiante] = inscripciones_estudiante
        
        print(f"Se generaron {id_inscripcion - 1} inscripciones simuladas")
        
        # Opcionalmente, guardar las inscripciones simuladas en CSV
        self.guardar_inscripciones_simuladas()
        
        return self.inscripciones

    def priorizar_materias_para_inscripcion(self, materias_disponibles, cuatrimestre_actual, max_materias):
        """Prioriza materias para inscripción, dando prioridad a las de cuatrimestres anteriores."""
        # Agrupar por cuatrimestre
        materias_por_cuatrimestre = {}
        for id_materia in materias_disponibles:
            materia = self.materias.get(id_materia)
            if not materia:
                continue
                
            if materia.cuatrimestre not in materias_por_cuatrimestre:
                materias_por_cuatrimestre[materia.cuatrimestre] = []
                
            materias_por_cuatrimestre[materia.cuatrimestre].append(id_materia)
        
        # Ordenar cuatrimestres (primero los anteriores)
        cuatrimestres_ordenados = sorted(materias_por_cuatrimestre.keys())
        
        # Seleccionar materias priorizando las de cuatrimestres anteriores
        materias_seleccionadas = []
        for cuatrimestre in cuatrimestres_ordenados:
            materias_cuatrimestre = materias_por_cuatrimestre[cuatrimestre]
            random.shuffle(materias_cuatrimestre)  # Para variedad
            
            for id_materia in materias_cuatrimestre:
                materias_seleccionadas.append(id_materia)
                if len(materias_seleccionadas) >= max_materias:
                    return materias_seleccionadas
        
        return materias_seleccionadas
    
    def cargar_materias(self):
        """Carga las materias desde materias.csv."""
        ruta = os.path.join(self.data_dir, "materias.csv")
        df = pd.read_csv(ruta)
        
        for _, row in df.iterrows():
            materia = Materia(
                id_materia=row['id_materia'],
                nombre=row['nombre'],
                cuatrimestre=row['cuatrimestre'],
                creditos=row['creditos'],
                horas_totales=row['horas_totales'],
                tipo=row['tipo']
            )
            self.materias[materia.id] = materia
    
    def cargar_seriacion(self):
        """Carga las relaciones de seriación desde seriacion.csv."""
        ruta = os.path.join(self.data_dir, "seriacion.csv")
        df = pd.read_csv(ruta)
        
        for _, row in df.iterrows():
            id_materia = row['id_materia']
            id_prerequisito = row['id_prerequisito']
            
            if id_materia not in self.seriacion:
                self.seriacion[id_materia] = []
            
            self.seriacion[id_materia].append(id_prerequisito)
    
    def cargar_dependencias_proyectos(self):
        """Carga las dependencias de proyectos desde dependencias_proyectos.csv."""
        ruta = os.path.join(self.data_dir, "dependencias_proyectos.csv")
        df = pd.read_csv(ruta)
        
        for _, row in df.iterrows():
            id_proyecto = row['id_proyecto']
            id_materia_dependiente = row['id_materia_dependiente']
            
            if id_proyecto not in self.dependencias_proyectos:
                self.dependencias_proyectos[id_proyecto] = []
            
            self.dependencias_proyectos[id_proyecto].append(id_materia_dependiente)
    
    def cargar_grupos(self):
        """Carga los grupos desde grupos.csv."""
        ruta = os.path.join(self.data_dir, "grupos.csv")
        df = pd.read_csv(ruta)
        
        for _, row in df.iterrows():
            grupo = Grupo(
                id_grupo=row['id_grupo'],
                id_materia=row['id_materia'],
                profesor=row['profesor'],
                cupo_maximo=row['cupo_maximo'],
                cupo_actual=row['cupo_actual']
            )
            self.grupos[grupo.id] = grupo
    
    def cargar_horarios(self):
        """Carga los horarios desde horarios.csv."""
        ruta = os.path.join(self.data_dir, "horarios.csv")
        df = pd.read_csv(ruta)
        
        for _, row in df.iterrows():
            id_grupo = row['id_grupo']
            horario = (row['dia'], row['hora_inicio'], row['hora_fin'], row['aula'])
            
            if id_grupo not in self.horarios:
                self.horarios[id_grupo] = []
            
            self.horarios[id_grupo].append(horario)
        
        # Asignar los horarios a cada grupo
        for id_grupo, horarios in self.horarios.items():
            if id_grupo in self.grupos:
                self.grupos[id_grupo].horarios = horarios
    
    def cargar_estudiantes(self):
        """Carga los estudiantes desde estudiantes.csv."""
        ruta = os.path.join(self.data_dir, "estudiantes.csv")
        df = pd.read_csv(ruta)
        
        for _, row in df.iterrows():
            estudiante = Estudiante(
                id_estudiante=row['id_estudiante'],
                nombre=row['nombre'],
                cuatrimestre=row['cuatrimestre_actual'],
                status=row['status'],
                creditos_acumulados=row['creditos_acumulados'],
                max_creditos=row['max_creditos']
            )
            self.estudiantes[estudiante.id] = estudiante
    
    def cargar_historial_academico(self):
        """Carga el historial académico desde historial_academico.csv."""
        ruta = os.path.join(self.data_dir, "historial_academico.csv")
        df = pd.read_csv(ruta)
        
        for _, row in df.iterrows():
            id_estudiante = row['id_estudiante']
            id_materia = row['id_materia']
            aprobada = row['aprobada']
            
            if id_estudiante not in self.historial_academico:
                self.historial_academico[id_estudiante] = []
            
            self.historial_academico[id_estudiante].append({
                'id_materia': id_materia,
                'calificacion': row['calificacion'],
                'cuatrimestre': row['cuatrimestre'],
                'aprobada': aprobada
            })
            
            # Actualizar materias aprobadas en el estudiante
            if aprobada and id_estudiante in self.estudiantes:
                self.estudiantes[id_estudiante].materias_aprobadas.add(id_materia)
    
    def cargar_preferencias(self):
        """Carga las preferencias desde preferencias_estudiante.csv."""
        ruta = os.path.join(self.data_dir, "preferencias_estudiante.csv")
        df = pd.read_csv(ruta)
        
        for _, row in df.iterrows():
            id_estudiante = row['id_estudiante']
            
            # Parsear días preferidos (convertir de string a lista de enteros)
            dias_preferidos_str = str(row['dias_preferidos'])
            dias_preferidos = []
            if dias_preferidos_str:
                try:
                    dias_preferidos = [int(d.strip()) for d in dias_preferidos_str.split(',') if d.strip()]
                except:
                    dias_preferidos = []
            
            # Parsear profesores preferidos
            profesores_preferidos_str = str(row['profesores_preferidos'])
            profesores_preferidos = []
            if profesores_preferidos_str:
                profesores_preferidos = [p.strip() for p in profesores_preferidos_str.split(',') if p.strip()]
            
            self.preferencias[id_estudiante] = {
                'preferencia_hora': row['preferencia_hora'],
                'dias_preferidos': dias_preferidos,
                'profesores_preferidos': profesores_preferidos
            }
            
            # Actualizar preferencias en el estudiante
            if id_estudiante in self.estudiantes:
                self.estudiantes[id_estudiante].preferencias = self.preferencias[id_estudiante]
    
    def obtener_estudiante(self, id_estudiante):
        """Obtiene un estudiante por su ID."""
        return self.estudiantes.get(id_estudiante)
    
    def obtener_materias_disponibles(self, estudiante):
        """Obtiene las materias que un estudiante puede cursar."""
        from services.optimizador import Optimizador
        
        optimizador = Optimizador(
            materias=self.materias,
            grupos=self.grupos,
            seriacion=self.seriacion,
            dependencias_proyectos=self.dependencias_proyectos
        )
        
        return optimizador.get_materias_disponibles(estudiante)