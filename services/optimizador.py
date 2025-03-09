import random
import numpy as np
from typing import List, Dict, Set, Tuple
from models.materia import Materia
from models.grupo import Grupo
from models.estudiante import Estudiante
from models.horario import Horario
import copy

class Optimizador:
    """Clase que implementa el algoritmo genético para optimizar la carga académica."""
    
    def __init__(self, materias, grupos, seriacion, dependencias_proyectos):
        """Inicializa el optimizador con los datos necesarios."""
        self.materias = materias or {}
        self.grupos = grupos or {}
        self.seriacion = seriacion or {}
        self.dependencias_proyectos = dependencias_proyectos or {}
        
        # Mapeo de materias a grupos disponibles
        self.materia_a_grupos = {}
        
        # Verificar que hay grupos válidos
        if self.grupos:
            for id_grupo, grupo in self.grupos.items():
                # Verificar que el grupo tiene un id_materia válido
                if hasattr(grupo, 'id_materia') and grupo.id_materia is not None:
                    if grupo.id_materia not in self.materia_a_grupos:
                        self.materia_a_grupos[grupo.id_materia] = []
                    self.materia_a_grupos[grupo.id_materia].append(id_grupo)
    
    def get_materias_disponibles(self, estudiante: Estudiante) -> List[int]:
        """Obtiene las materias que el estudiante puede cursar basado en su historial y seriación."""
        disponibles = []
        
        # Obtener IDs de materias de estadía
        estadias = [id_materia for id_materia, materia in self.materias.items() 
                if materia.tipo == "Estadía"]
        
        # Verificar si el estudiante ya está cursando alguna estadía
        # (si estamos en modo simulación para planificación futura)
        inscripciones_simuladas = getattr(estudiante, 'inscripciones_simuladas', [])
        cursando_estadia = any(id_materia in estadias for id_materia in inscripciones_simuladas)
        
        # Si el estudiante es regular, simplemente devolvemos todas las materias de su cuatrimestre actual
        # que no haya aprobado ya y que no tengan prerrequisitos pendientes
        if estudiante.es_regular():
            # Obtener todas las materias del cuatrimestre actual
            for id_materia, materia in self.materias.items():
                # Solo materias del cuatrimestre actual
                if materia.cuatrimestre == estudiante.cuatrimestre:
                    # Verificar que no haya aprobado la materia
                    if id_materia in estudiante.materias_aprobadas:
                        continue
                    
                    # Verificar seriación (prerrequisitos)
                    if id_materia in self.seriacion:
                        prerequisitos_cumplidos = True
                        for prerequisito in self.seriacion[id_materia]:
                            if prerequisito not in estudiante.materias_aprobadas:
                                prerequisitos_cumplidos = False
                                break
                        
                        if not prerequisitos_cumplidos:
                            continue
                    
                    # Verificar que haya grupos disponibles para esta materia
                    if id_materia in self.materia_a_grupos and self.materia_a_grupos[id_materia]:
                        disponibles.append(id_materia)
                        
            return disponibles
        
        # Para estudiantes irregulares, aplicamos la lógica original más flexible
        for id_materia, materia in self.materias.items():
            # Verificar que no haya aprobado la materia
            if id_materia in estudiante.materias_aprobadas:
                continue
            
            # Si el estudiante está cursando estadía, no puede tomar otras materias
            if cursando_estadia and id_materia not in estadias:
                continue
                
            # Si la materia es estadía pero otra estadía ya está siendo cursada, no disponible
            if materia.tipo == "Estadía" and cursando_estadia:
                continue
            
            # Alumnos irregulares pueden tomar materias de cuatrimestres anteriores o actuales
            if materia.cuatrimestre > estudiante.cuatrimestre:
                continue
            
            # Reglas específicas para estadías
            if materia.tipo == "Estadía":
                # Estadía 1 (cuatrimestre 6)
                if materia.cuatrimestre == 6:
                    # Solo disponible a partir del 6º cuatrimestre
                    if estudiante.cuatrimestre < 6:
                        continue
                    
                    # Verificar que haya aprobado Proyecto Integrador 2 (ID 35)
                    proyecto_integrador_2_id = 35
                    if proyecto_integrador_2_id not in estudiante.materias_aprobadas:
                        continue
                    
                    # Verificar que haya aprobado las materias dependientes del Proyecto Integrador 2
                    dependencias_proyecto = self.dependencias_proyectos.get(proyecto_integrador_2_id, [])
                    dependencias_cumplidas = True
                    for dep_id in dependencias_proyecto:
                        if dep_id not in estudiante.materias_aprobadas:
                            dependencias_cumplidas = False
                            break
                    
                    if not dependencias_cumplidas:
                        continue
                
                # Estadía 2 (cuatrimestre 10)
                elif materia.cuatrimestre == 10:
                    # Solo disponible en el último cuatrimestre
                    if estudiante.cuatrimestre < 10:
                        continue
            
            # Verificar seriación
            if id_materia in self.seriacion:
                prerequisitos_cumplidos = True
                for prerequisito in self.seriacion[id_materia]:
                    if prerequisito not in estudiante.materias_aprobadas:
                        prerequisitos_cumplidos = False
                        break
                
                if not prerequisitos_cumplidos:
                    continue
            
            # Verificar dependencias de proyectos
            if materia.tipo == "Proyecto Integrador":
                dependencias_cumplidas = True
                for dep_materia in self.dependencias_proyectos.get(id_materia, []):
                    if dep_materia not in estudiante.materias_aprobadas:
                        dependencias_cumplidas = False
                        break
                
                if not dependencias_cumplidas:
                    continue
            
            # Verificar que haya grupos disponibles para esta materia
            if id_materia in self.materia_a_grupos and self.materia_a_grupos[id_materia]:
                disponibles.append(id_materia)
        
        return disponibles
    
    def hay_conflicto_horario(self, horarios1, horarios2):
        """Verifica si hay conflicto entre dos conjuntos de horarios."""
        # Protección contra nulos
        if not horarios1 or not horarios2:
            return False
            
        try:
            for dia1, inicio1, fin1, _ in horarios1:
                for dia2, inicio2, fin2, _ in horarios2:
                    if dia1 == dia2:  # Mismo día
                        # Convertir a enteros si son strings
                        if isinstance(inicio1, str):
                            inicio1 = int(inicio1.split(':')[0])
                        if isinstance(fin1, str):
                            fin1 = int(fin1.split(':')[0])
                        if isinstance(inicio2, str):
                            inicio2 = int(inicio2.split(':')[0])
                        if isinstance(fin2, str):
                            fin2 = int(fin2.split(':')[0])
                        
                        # Verificar superposición de horarios
                        if (inicio1 <= inicio2 < fin1) or (inicio1 < fin2 <= fin1) or \
                        (inicio2 <= inicio1 < fin2) or (inicio2 < fin1 <= fin2):
                            return True
        except (ValueError, TypeError, IndexError) as e:
            print(f"Error al verificar conflicto de horarios: {e}")
            return False  # En caso de error, asumir que no hay conflicto
            
        return False
    
    def generar_poblacion_inicial_con_grupos(self, estudiante, tamano_poblacion, grupos_disponibles):
        """Genera una población inicial basada en grupos específicos."""
        poblacion = []
        
        # Verificar que haya grupos disponibles
        if not grupos_disponibles:
            print("Advertencia: No hay grupos disponibles para generar población inicial")
            return poblacion
        
        # Agrupamos los grupos por materia
        grupos_por_materia = {}
        for id_grupo in grupos_disponibles:
            grupo = self.grupos.get(id_grupo)
            if not grupo:  # Protección contra grupos inválidos
                continue
                
            id_materia = grupo.id_materia
            if id_materia not in grupos_por_materia:
                grupos_por_materia[id_materia] = []
            grupos_por_materia[id_materia].append(id_grupo)
        
        # Lista de materias disponibles
        materias_disponibles = list(grupos_por_materia.keys())
        
        # Si no hay materias disponibles, no podemos generar población
        if not materias_disponibles:
            print("Advertencia: No hay materias disponibles para generar población inicial")
            return poblacion
        
        # Intentos máximos para generar población válida
        max_intentos = tamano_poblacion * 5  # Aumentamos el número de intentos
        intentos = 0
        
        while len(poblacion) < tamano_poblacion and intentos < max_intentos:
            intentos += 1
            
            # Seleccionar aleatoriamente un subconjunto de materias disponibles
            # Nos aseguramos de que al menos intentamos tomar 2 materias si es posible
            max_materias = min(8, len(materias_disponibles))
            min_materias = min(2, max_materias)  # Al menos 2 materias o todas si hay menos de 2
            
            if max_materias < 1:  # Si no hay materias, no podemos hacer nada
                break
                
            num_materias = random.randint(min_materias, max_materias)
            materias_seleccionadas = random.sample(materias_disponibles, num_materias)
            
            # Para cada materia, seleccionar un grupo disponible
            horario = []
            materias_validas = True
            
            for id_materia in materias_seleccionadas:
                if id_materia not in grupos_por_materia:
                    materias_validas = False
                    break
                    
                grupos_de_materia = grupos_por_materia[id_materia].copy()
                if not grupos_de_materia:  # Protección contra lista vacía
                    materias_validas = False
                    break
                    
                random.shuffle(grupos_de_materia)
                
                grupo_valido = False
                for id_grupo in grupos_de_materia:
                    if id_grupo not in self.grupos:  # Protección contra grupos inválidos
                        continue
                        
                    grupo = self.grupos[id_grupo]
                    
                    # Verificar cupo (con flexibilidad)
                    if hasattr(grupo, 'tiene_cupo') and not grupo.tiene_cupo():
                        continue
                    
                    # Verificar conflictos de horario con materias ya seleccionadas
                    conflicto = False
                    for id_grupo_seleccionado in horario:
                        if id_grupo_seleccionado not in self.grupos:  # Protección
                            continue
                            
                        if self.hay_conflicto_horario(
                            grupo.horarios if hasattr(grupo, 'horarios') else [], 
                            self.grupos[id_grupo_seleccionado].horarios if hasattr(self.grupos[id_grupo_seleccionado], 'horarios') else []
                        ):
                            conflicto = True
                            break
                    
                    if not conflicto:
                        horario.append(id_grupo)
                        grupo_valido = True
                        break
                
                if not grupo_valido:
                    materias_validas = False
                    break
            
            if materias_validas and horario:
                poblacion.append(horario)
        
        # Si no pudimos generar ninguna solución válida
        if not poblacion:
            print("Advertencia: No se pudo generar ninguna solución válida en la población inicial")
            # Crear al menos un horario vacío para que el algoritmo pueda continuar
            poblacion.append([])
        
        # Si no pudimos generar suficientes horarios, rellenar con copias
        # pero solo si hay al menos un horario válido
        while len(poblacion) < tamano_poblacion and len(poblacion) > 0:
            poblacion.append(random.choice(poblacion).copy())
        
        return poblacion
    
    def calcular_fitness(self, estudiante: Estudiante, horario: List[int]) -> float:
        """Calcula el valor de fitness para un horario específico."""
        if not horario:
            return 0.0
        
        # Identificar si hay materias de estadía en el horario
        estadias_en_horario = []
        for id_grupo in horario:
            grupo = self.grupos.get(id_grupo)
            if grupo and grupo.id_materia in self.materias:
                materia = self.materias[grupo.id_materia]
                if materia.tipo == "Estadía":
                    estadias_en_horario.append(materia.id)
        
        # 1. Verificar reglas de estadía
        if estadias_en_horario:
            # Si hay una estadía, debe ser la única materia
            if len(horario) > 1:
                return 0.0  # Horario inválido si hay más materias además de estadía
            # Si hay más de una estadía, es inválido
            if len(estadias_en_horario) > 1:
                return 0.0  # No se puede cursar más de una estadía a la vez
            
            # Si llegamos aquí, hay exactamente una estadía y es la única materia (correcto)
            return 1.0  # Máximo fitness para un horario con estadía
        
        # 2. Verificar número de materias según tipo de estudiante
        materias_inscritas = set(self.grupos[id_grupo].id_materia for id_grupo in horario)
        if estudiante.es_regular():
            # Regulares deben tener exactamente 7 materias, menos es subóptimo
            if len(materias_inscritas) < 7:
                penalizacion_materias = 1 - (7 - len(materias_inscritas)) * 0.1
            elif len(materias_inscritas) > 7:
                return 0.0  # Inválido tener más de 7 materias
            else:
                penalizacion_materias = 1.0  # Óptimo: exactamente 7 materias
        else:
            # Irregulares: flexible, pero con límite máximo
            max_materias_irregular = 5
            if len(materias_inscritas) > max_materias_irregular:
                return 0.0  # Inválido exceder el máximo
            else:
                # Premiar más materias, hasta el máximo permitido
                penalizacion_materias = len(materias_inscritas) / max_materias_irregular
        
        # 3. Verificar que no exceda el máximo de créditos (prioridad alta)
        total_creditos = 0
        for id_grupo in horario:
            id_materia = self.grupos[id_grupo].id_materia
            total_creditos += self.materias[id_materia].creditos
        
        if total_creditos > estudiante.max_creditos:
            return 0.0  # Horario inválido
        
        # 4. Evaluar balance de carga por día (prioridad alta)
        carga_por_dia = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}  # Lunes a Viernes
        
        for id_grupo in horario:
            for dia, _, _, _ in self.grupos[id_grupo].horarios:
                if 1 <= dia <= 5:  # Solo consideramos días hábiles
                    carga_por_dia[dia] += 1
        
        desviacion_estandar = np.std(list(carga_por_dia.values()))
        
        # 5. Priorizar materias de cuatrimestres anteriores para irregulares (prioridad alta)
        prioridad_materias = 0
        if not estudiante.es_regular():
            for id_grupo in horario:
                id_materia = self.grupos[id_grupo].id_materia
                cuatrimestre_materia = self.materias[id_materia].cuatrimestre
                
                # Mayor prioridad a materias de cuatrimestres más antiguos
                if cuatrimestre_materia < estudiante.cuatrimestre:
                    prioridad_materias += (estudiante.cuatrimestre - cuatrimestre_materia)
        
        # 6. Satisfacción de preferencias del estudiante (prioridad baja)
        satisfaccion_preferencias = 0
        
        # Preferencia de horario (mañana, tarde, noche)
        if 'preferencia_hora' in estudiante.preferencias:
            pref_horario = estudiante.preferencias['preferencia_hora']
            
            for id_grupo in horario:
                for _, hora_inicio, _, _ in self.grupos[id_grupo].horarios:
                    if isinstance(hora_inicio, str):
                        hora = int(hora_inicio.split(':')[0])
                    else:
                        hora = hora_inicio
                    
                    if (pref_horario == 'mañana' and 8 <= hora < 12) or \
                    (pref_horario == 'tarde' and 12 <= hora < 18) or \
                    (pref_horario == 'noche' and hora >= 18):
                        satisfaccion_preferencias += 1
        
        # Preferencia de días (peso reducido)
        if 'dias_preferidos' in estudiante.preferencias:
            dias_pref = estudiante.preferencias['dias_preferidos']
            dias_asignados = set()
            
            for id_grupo in horario:
                for dia, _, _, _ in self.grupos[id_grupo].horarios:
                    dias_asignados.add(dia)
            
            # Calcular preferencias satisfechas
            dias_coincidentes = sum(1 for dia in dias_asignados if dia in dias_pref)
            if dias_coincidentes > 0:
                # Dar algún valor, pero menor al de otras preferencias
                satisfaccion_preferencias += (dias_coincidentes / len(dias_asignados)) * 0.5
        
        # Construir fitness final (ponderado)
        if estudiante.es_regular():
            # Para regulares, priorizar tener 7 materias y balance de carga
            fitness = (
                0.40 * penalizacion_materias +                # Número correcto de materias (muy alto)
                0.35 * (1 / (1 + desviacion_estandar)) +      # Balance de carga (alto)
                0.15 * (total_creditos / estudiante.max_creditos) + # Uso eficiente de créditos (medio)
                0.10 * satisfaccion_preferencias              # Preferencias (bajo)
            )
        else:
            # Para irregulares, priorizar materias atrasadas y balance de carga
            fitness = (
                0.30 * penalizacion_materias +                # Número de materias (alto)
                0.30 * (1 / (1 + desviacion_estandar)) +      # Balance de carga (alto)
                0.30 * prioridad_materias +                   # Materias atrasadas (alto)
                0.10 * satisfaccion_preferencias              # Preferencias (bajo)
            )
        
        return fitness
    
    def seleccionar_padres(self, poblacion, fitness, num_padres):
        """Selecciona padres para reproducción usando selección por torneo.
        
        Args:
            poblacion (list): Lista de individuos (horarios).
            fitness (list): Lista de valores de fitness correspondientes a cada individuo.
            num_padres (int): Número de padres a seleccionar.
            
        Returns:
            list: Lista de padres seleccionados.
        """
        padres = []
        
        # Verificar que la población no esté vacía
        if not poblacion or len(poblacion) == 0:
            return padres  # Retornar lista vacía si no hay población
        
        for _ in range(num_padres):
            # Asegurarse de que hay al menos un individuo para el torneo
            if len(poblacion) == 0:
                break
                
            # Determinar tamaño del torneo (entre 1 y 3, dependiendo del tamaño de la población)
            tamano_torneo = min(3, len(poblacion))
            if tamano_torneo == 0:
                break
                
            # Seleccionar individuos aleatoriamente para el torneo
            try:
                indices_torneo = random.sample(range(len(poblacion)), tamano_torneo)
                
                # Encontrar el mejor
                mejor_idx = indices_torneo[0]
                for idx in indices_torneo[1:]:
                    if fitness[idx] > fitness[mejor_idx]:
                        mejor_idx = idx
                
                padres.append(poblacion[mejor_idx])
            except (ValueError, IndexError) as e:
                # Si hay algún error en el muestreo o con índices, registrarlo y continuar
                print(f"Error en selección de padres: {e}")
                continue
        
        return padres
    
    def cruzar(self, padre1: List[int], padre2: List[int]) -> Tuple[List[int], List[int]]:
        """Realiza cruza entre dos padres para generar dos hijos."""
        # Caso especial: si algún padre está vacío o tiene solo un elemento, 
        # simplemente devolvemos copias de los padres
        if not padre1 or not padre2 or len(padre1) <= 1 or len(padre2) <= 1:
            return padre1.copy(), padre2.copy()
        
        # Calculamos el punto de corte de manera segura
        max_punto_corte = min(len(padre1), len(padre2)) - 1
        
        # Verificación adicional para evitar rangos vacíos
        if max_punto_corte < 1:
            return padre1.copy(), padre2.copy()
        
        punto_corte = random.randint(1, max_punto_corte)
        
        hijo1 = padre1[:punto_corte] + padre2[punto_corte:]
        hijo2 = padre2[:punto_corte] + padre1[punto_corte:]
        
        return hijo1, hijo2
    
    def mutar(self, horario: List[int], tasa_mutacion: float, 
             estudiante: Estudiante) -> List[int]:
        """Aplica mutación a un horario."""
        if not horario or random.random() > tasa_mutacion:
            return horario
        
        # Elegir grupo a mutar
        idx_mutar = random.randint(0, len(horario) - 1)
        id_grupo_actual = horario[idx_mutar]
        id_materia_actual = self.grupos[id_grupo_actual].id_materia
        
        # Intentar reemplazar por otro grupo de la misma materia
        otros_grupos = [id_grupo for id_grupo in self.materia_a_grupos.get(id_materia_actual, []) 
                       if id_grupo != id_grupo_actual]
        
        if otros_grupos:
            nuevo_grupo = random.choice(otros_grupos)
            
            # Verificar conflictos de horario
            conflicto = False
            for id_grupo in horario:
                if id_grupo != id_grupo_actual and self.hay_conflicto_horario(
                    self.grupos[nuevo_grupo].horarios, self.grupos[id_grupo].horarios):
                    conflicto = True
                    break
            
            if not conflicto:
                horario_mutado = horario.copy()
                horario_mutado[idx_mutar] = nuevo_grupo
                return horario_mutado
        
        # Si no podemos mutar el grupo, intentar reemplazar la materia
        materias_disponibles = self.get_materias_disponibles(estudiante)
        materias_actuales = {self.grupos[id_grupo].id_materia for id_grupo in horario}
        nuevas_materias = [m for m in materias_disponibles if m not in materias_actuales]
        
        if nuevas_materias:
            nueva_materia = random.choice(nuevas_materias)
            grupos_nuevos = self.materia_a_grupos.get(nueva_materia, [])
            
            if grupos_nuevos:
                random.shuffle(grupos_nuevos)
                for nuevo_grupo in grupos_nuevos:
                    # Verificar cupo
                    if not self.grupos[nuevo_grupo].tiene_cupo():
                        continue
                    
                    # Verificar conflictos de horario
                    conflicto = False
                    for id_grupo in horario:
                        if id_grupo != id_grupo_actual and self.hay_conflicto_horario(
                            self.grupos[nuevo_grupo].horarios, self.grupos[id_grupo].horarios):
                            conflicto = True
                            break
                    
                    if not conflicto:
                        horario_mutado = horario.copy()
                        horario_mutado[idx_mutar] = nuevo_grupo
                        return horario_mutado
        
        return horario
    
    
    def generar_horario_semanal(self, horario):
        """Genera una representación del horario semanal para visualización."""
        dias = {1: "Lunes", 2: "Martes", 3: "Miércoles", 4: "Jueves", 5: "Viernes"}
        horas = list(range(7, 22))  # De 7am a 9pm
        
        horario_semanal = {dia: {hora: None for hora in horas} for dia in dias.keys()}
        
        # Verificar que el horario no sea None
        if horario is None:
            return {dia_nombre: {f"{hora}:00": None for hora in horas} 
                    for dia, dia_nombre in dias.items()}
        
        for id_grupo in horario:
            grupo = self.grupos.get(id_grupo)
            if not grupo:
                continue
                
            materia = self.materias.get(grupo.id_materia) if hasattr(grupo, 'id_materia') else None
            if not materia:
                continue
                
            # Verificar que el grupo tiene horarios
            if not hasattr(grupo, 'horarios') or not grupo.horarios:
                continue
                
            for dia, hora_inicio, hora_fin, aula in grupo.horarios:
                # Verificar que día está en el rango válido
                if dia not in dias:
                    continue
                    
                # Convertir a enteros si son strings
                try:
                    if isinstance(hora_inicio, str):
                        inicio_hora = int(hora_inicio.split(':')[0])
                    else:
                        inicio_hora = hora_inicio
                        
                    if isinstance(hora_fin, str):
                        fin_hora = int(hora_fin.split(':')[0])
                    else:
                        fin_hora = hora_fin
                except (ValueError, TypeError) as e:
                    print(f"Error al convertir horas: {e}")
                    continue
                
                # Verificar que las horas están en el rango válido
                if inicio_hora < 7 or fin_hora > 22 or inicio_hora >= fin_hora:
                    continue
                
                info_clase = {
                    "materia": materia.nombre,
                    "profesor": grupo.profesor,
                    "aula": aula,
                    "grupo": grupo.id
                }
                
                for hora in range(inicio_hora, fin_hora):
                    if dia in horario_semanal and hora in horario_semanal[dia]:
                        horario_semanal[dia][hora] = info_clase
        
        # Convertir a formato más amigable para la API
        formato_api = {}
        for dia, horas_dict in horario_semanal.items():
            dia_nombre = dias.get(dia, f"Día {dia}")
            formato_api[dia_nombre] = {}
            for hora, info in horas_dict.items():
                formato_api[dia_nombre][f"{hora}:00"] = info
        
        return formato_api
    
    def _generar_horario_semanal_simple(self, materias_con_horarios):
        """Genera un horario semanal a partir de materias y sus horarios.
        
        Args:
            materias_con_horarios: Iterable de tuplas (id_materia, horarios)
            
        Returns:
            dict: Horario semanal en formato API
        """
        dias_nombre = {1: "Lunes", 2: "Martes", 3: "Miércoles", 4: "Jueves", 5: "Viernes"}
        slots_disponibles = ["8:00", "10:00", "12:00", "14:00", "16:00", "18:00"]
        
        # Inicializar horario vacío
        horario = {
            dia_nombre: {slot: None for slot in slots_disponibles}
            for dia_nombre in dias_nombre.values()
        }
        
        # Asignar materias a los slots
        for id_materia, horarios_materia in materias_con_horarios:
            if not horarios_materia:
                continue
                
            materia = self.materias.get(id_materia)
            if not materia:
                continue
                
            for dia, hora_inicio, hora_fin, aula in horarios_materia:
                if dia not in dias_nombre:
                    continue
                    
                dia_nombre = dias_nombre[dia]
                
                # Asignar al slot más cercano
                slot_asignado = None
                for slot in slots_disponibles:
                    if slot.startswith(hora_inicio.split(':')[0]) or slot == f"{int(hora_inicio.split(':')[0])}:00":
                        slot_asignado = slot
                        break
                
                if slot_asignado:
                    horario[dia_nombre][slot_asignado] = {
                        "materia": materia.nombre,
                        "profesor": "Por asignar",
                        "aula": aula,
                        "grupo": 0
                    }
        
        return horario
    
    def simular_planificacion_cuatrimestre(self, estudiante, materias_disponibles, num_cuatrimestre):
        """Simula la planificación de un cuatrimestre sin ejecutar el algoritmo genético completo.
        
        Esta función es útil para la planificación a largo plazo donde no necesitamos
        la precisión completa del algoritmo genético, sino una aproximación razonable.
        
        Args:
            estudiante (Estudiante): Objeto estudiante para el que se planifica.
            materias_disponibles (List[int]): Lista de IDs de materias disponibles.
            num_cuatrimestre (int): Número de cuatrimestre a planificar.
            
        Returns:
            dict: Diccionario con información del cuatrimestre planificado.
        """
        if not materias_disponibles:
            return {
                "cuatrimestre": num_cuatrimestre,
                "materias_inscritas": [],
                "creditos_totales": 0,
                "num_materias": 0,
                "horario_semanal": {},
                "carga_por_dia": {dia: 0 for dia in range(1, 6)},
                "advertencia": "No hay materias disponibles para este cuatrimestre"
            }
        
        # Verificar si hay materias de estadía
        estadias = [id_materia for id_materia in materias_disponibles 
                if self.materias.get(id_materia) and self.materias[id_materia].tipo == "Estadía"]
        
        # Si hay estadías, solo planificar la estadía
        if estadias:
            id_estadia = estadias[0]  # Tomar la primera estadía disponible
            materia_estadia = self.materias[id_estadia]
            
            return {
                "cuatrimestre": num_cuatrimestre,
                "materias_inscritas": [{
                    "id_materia": id_estadia,
                    "nombre_materia": materia_estadia.nombre,
                    "id_grupo": 0,  # Grupo simulado
                    "profesor": "Por asignar",
                    "creditos": materia_estadia.creditos,
                    "cuatrimestre": materia_estadia.cuatrimestre,
                    "tipo": materia_estadia.tipo,
                    "horarios": [(1, "08:00", "10:00", "A101")]  # Horario simulado
                }],
                "creditos_totales": materia_estadia.creditos,
                "num_materias": 1,
                "horario_semanal": self._generar_horario_semanal_simple([(id_estadia, [(1, "08:00", "10:00", "A101")])]),
                "carga_por_dia": {1: 1, 2: 0, 3: 0, 4: 0, 5: 0}
            }
        
        # Determinar número exacto de materias
        # Para regulares siempre 7, para irregulares hasta 5 (según disponibilidad)
        if estudiante.es_regular():
            # Asegurar que tengamos exactamente 7 materias si están disponibles
            num_materias = min(7, len(materias_disponibles))
            # Si no hay 7 materias disponibles, emitir advertencia
            if num_materias < 7:
                print(f"Advertencia: Solo hay {num_materias} materias disponibles para el estudiante regular en el cuatrimestre {num_cuatrimestre}")
        else:
            # Para irregulares, máximo 5 materias
            num_materias = min(5, len(materias_disponibles))
        
        # Tomar las materias disponibles limitadas según el tipo de estudiante
        materias_a_cursar = materias_disponibles[:num_materias]
        
        # Acumular información de las materias
        materias_inscritas = []
        creditos_totales = 0
        horarios_por_materia = {}
        
        # Distribuir materias en los días de la semana
        dias_de_semana = list(range(1, 6))  # 1=Lunes a 5=Viernes
        
        for id_materia in materias_a_cursar:
            materia = self.materias.get(id_materia)
            if not materia:
                continue
                
            # Asignar horarios de manera inteligente para evitar conflictos
            # Para materias de más créditos (5+), asignar 2 días
            # Para materias de menos créditos, asignar 1 día
            dias_asignados = []
            
            # Decidir cuántos días necesita esta materia
            num_dias_necesarios = 2 if materia.creditos >= 5 else 1
            
            # Intentar asignar días balanceados (para no sobrecargar un solo día)
            dias_disponibles = dias_de_semana.copy()
            random.shuffle(dias_disponibles)
            
            # Recorrer días en orden aleatorio hasta encontrar suficientes disponibles
            for _ in range(num_dias_necesarios):
                if dias_disponibles:
                    dias_asignados.append(dias_disponibles.pop(0))
            
            # Si no hay suficientes días disponibles, usar los que quedan
            while len(dias_asignados) < num_dias_necesarios and dias_de_semana:
                dia_aleatorio = random.choice(dias_de_semana)
                if dia_aleatorio not in dias_asignados:
                    dias_asignados.append(dia_aleatorio)
            
            # Asignar horarios para la materia
            horarios_materia = []
            for dia in dias_asignados:
                # Asignar un horario fijo para simplificar
                horarios_materia.append((dia, "08:00", "10:00", "A101"))
            
            # Guardar horarios de esta materia
            horarios_por_materia[id_materia] = horarios_materia
            
            # Agregar a materias inscritas
            materias_inscritas.append({
                "id_materia": id_materia,
                "nombre_materia": materia.nombre,
                "id_grupo": 0,  # Grupo simulado
                "profesor": "Por asignar",
                "creditos": materia.creditos,
                "cuatrimestre": materia.cuatrimestre,
                "tipo": materia.tipo,
                "horarios": horarios_materia
            })
            
            creditos_totales += materia.creditos
        
        # Calcular carga por día
        carga_por_dia = {dia: 0 for dia in range(1, 6)}
        for id_materia, horarios in horarios_por_materia.items():
            for dia, _, _, _ in horarios:
                if 1 <= dia <= 5:
                    carga_por_dia[dia] += 1
        
        # Generar horario semanal
        horario_semanal = self._generar_horario_semanal_simple(horarios_por_materia.items())
        
        return {
            "cuatrimestre": num_cuatrimestre,
            "materias_inscritas": materias_inscritas,
            "creditos_totales": creditos_totales,
            "num_materias": len(materias_inscritas),
            "horario_semanal": horario_semanal,
            "carga_por_dia": carga_por_dia
        }
    
    def verificar_prerequisitos(self, id_materia, materias_aprobadas):
        """Verifica si una materia cumple con todos sus prerrequisitos.
        
        Args:
            id_materia: ID de la materia a verificar
            materias_aprobadas: Conjunto de IDs de materias aprobadas
            
        Returns:
            bool: True si cumple con todos los prerrequisitos, False en caso contrario
        """
        # Verificar seriación
        if id_materia in self.seriacion:
            for prerequisito in self.seriacion[id_materia]:
                if prerequisito not in materias_aprobadas:
                    return False
        
        # Verificar dependencias de proyectos
        materia = self.materias.get(id_materia)
        if materia and materia.tipo == "Proyecto Integrador":
            for dep_materia in self.dependencias_proyectos.get(id_materia, []):
                if dep_materia not in materias_aprobadas:
                    return False
        
        return True 
    
    def verificar_prerequisitos_para_estadia(self, id_estadia, materias_aprobadas):
        """Verifica los prerrequisitos específicos para cursar una estadía.
        
        Args:
            id_estadia: ID de la estadía a verificar
            materias_aprobadas: Conjunto de IDs de materias aprobadas
            
        Returns:
            bool: True si cumple con los requisitos para cursar la estadía
        """
        materia = self.materias.get(id_estadia)
        if not materia or materia.tipo != "Estadía":
            return False
        
        # Estadía 1 (cuatrimestre 6)
        if materia.cuatrimestre == 6:
            # Verificar Proyecto Integrador 2 (ID 35)
            proyecto_integrador_2_id = 35
            if proyecto_integrador_2_id not in materias_aprobadas:
                return False
            
            # Verificar materias relacionadas con Proyecto Integrador 2
            materias_relacionadas = [32, 33, 34]  # IDs de las materias relacionadas
            for id_materia in materias_relacionadas:
                if id_materia not in materias_aprobadas:
                    return False
        
        # Estadía 2 (cuatrimestre 10)
        elif materia.cuatrimestre == 10:
            # Verificar Proyecto Integrador 3 (ID 57)
            proyecto_integrador_3_id = 57
            if proyecto_integrador_3_id not in materias_aprobadas:
                return False
        
        # Verificar seriación general
        return self.verificar_prerequisitos(id_estadia, materias_aprobadas)
    
    def planificar_trayectoria_completa(self, estudiante):
        """Genera un plan completo de trayectoria académica hasta la graduación."""
        MAX_CUATRIMESTRES = 15  # Límite máximo de cuatrimestres permitidos
        
        try:
            # Obtener todas las materias del plan de estudios organizadas por cuatrimestre
            materias_por_cuatrimestre = {}
            for id_materia, materia in self.materias.items():
                if materia.cuatrimestre not in materias_por_cuatrimestre:
                    materias_por_cuatrimestre[materia.cuatrimestre] = []
                materias_por_cuatrimestre[materia.cuatrimestre].append(id_materia)
            
            # Determinar el cuatrimestre actual del estudiante
            cuatrimestre_actual = estudiante.cuatrimestre
            
            # Obtener todas las materias aprobadas
            materias_aprobadas = set(estudiante.materias_aprobadas)
            
            # Obtener todas las materias pendientes (no aprobadas) organizadas por cuatrimestre
            materias_pendientes_por_cuatrimestre = {}
            for cuatrimestre, materias in materias_por_cuatrimestre.items():
                materias_pendientes = [m for m in materias if m not in materias_aprobadas]
                if materias_pendientes:
                    materias_pendientes_por_cuatrimestre[cuatrimestre] = materias_pendientes
            
            # Calcular el total de materias pendientes
            total_materias_pendientes = sum(len(materias) for materias in materias_pendientes_por_cuatrimestre.values())
            
            # Inicializar la estructura del plan completo
            plan_completo = {
                "cuatrimestres_restantes": 0,
                "total_materias_pendientes": total_materias_pendientes,
                "plan_por_cuatrimestre": {},
                "estadisticas": {
                    "materias_aprobadas": len(materias_aprobadas),
                    "materias_pendientes": total_materias_pendientes,
                    "porcentaje_avance": round(len(materias_aprobadas) / max(1, (len(materias_aprobadas) + total_materias_pendientes)) * 100, 2)
                }
            }
            
            # Si no hay materias pendientes, el estudiante ya completó el plan
            if total_materias_pendientes == 0:
                plan_completo["mensaje"] = "El estudiante ha completado todas las materias del plan de estudios"
                return plan_completo
            
            # Organizar materias pendientes respetando seriaciones y dependencias
            # Empezamos desde el cuatrimestre actual y planificamos hacia adelante
            simulacion_aprobadas = set(materias_aprobadas)  # Materias que se consideran "aprobadas" en simulación
            cuatrimestre_planificacion = cuatrimestre_actual
            estudiante_simulado = copy.deepcopy(estudiante)  # Copia para simulación
            estudiante_simulado.inscripciones_simuladas = []  # Inicializar el atributo
            
            # Límite para evitar bucles infinitos
            max_ciclos = 20
            ciclo_actual = 0
            
            while materias_pendientes_por_cuatrimestre and cuatrimestre_planificacion <= MAX_CUATRIMESTRES and ciclo_actual < max_ciclos:
                ciclo_actual += 1
                
                # Actualizar el cuatrimestre del estudiante simulado
                estudiante_simulado.cuatrimestre = cuatrimestre_planificacion
                
                # Limpiar inscripciones simuladas anteriores
                estudiante_simulado.inscripciones_simuladas = []
                
                # Obtener materias de estadía disponibles para verificación especial
                estadias_disponibles = []
                for id_materia, materia in self.materias.items():
                    if (materia.tipo == "Estadía" and 
                        materia.cuatrimestre == cuatrimestre_planificacion and
                        id_materia not in simulacion_aprobadas):
                        
                        # Verificar prerrequisitos para Estadía
                        if self.verificar_prerequisitos_para_estadia(id_materia, simulacion_aprobadas):
                            estadias_disponibles.append(id_materia)
                
                # Si hay estadías disponibles y cumplen prerrequisitos, planificar solo la estadía
                if estadias_disponibles:
                    id_estadia = estadias_disponibles[0]  # Tomar la primera estadía disponible
                    materia_estadia = self.materias[id_estadia]
                    
                    # Planificar estadía
                    carga_cuatrimestre = {
                        "cuatrimestre": cuatrimestre_planificacion,
                        "materias_inscritas": [{
                            "id_materia": id_estadia,
                            "nombre_materia": materia_estadia.nombre,
                            "id_grupo": 0,  # Grupo simulado
                            "profesor": "Por asignar",
                            "creditos": materia_estadia.creditos,
                            "cuatrimestre": materia_estadia.cuatrimestre,
                            "tipo": materia_estadia.tipo,
                            "horarios": []
                        }],
                        "creditos_totales": materia_estadia.creditos,
                        "num_materias": 1,
                        "horario_semanal": {},
                        "carga_por_dia": {1:0, 2:0, 3:0, 4:0, 5:0}
                    }
                    
                    plan_completo["plan_por_cuatrimestre"][cuatrimestre_planificacion] = carga_cuatrimestre
                    simulacion_aprobadas.add(id_estadia)
                    
                    # Eliminar de pendientes
                    for cuatri in list(materias_pendientes_por_cuatrimestre.keys()):
                        if id_estadia in materias_pendientes_por_cuatrimestre[cuatri]:
                            materias_pendientes_por_cuatrimestre[cuatri].remove(id_estadia)
                            total_materias_pendientes -= 1
                    
                    # Ya no buscar más materias para este cuatrimestre
                    cuatrimestre_planificacion += 1
                    continue
                
                # CAMBIO IMPORTANTE: Para estudiantes regulares, tomar TODAS las materias del cuatrimestre actual
                if estudiante_simulado.es_regular():
                    # Obtener todas las materias pendientes de este cuatrimestre
                    materias_cuatrimestre = materias_por_cuatrimestre.get(cuatrimestre_planificacion, [])
                    materias_pendientes_cuatrimestre = [m for m in materias_cuatrimestre if m not in simulacion_aprobadas]
                    
                    # Verificar si hay materias pendientes para este cuatrimestre
                    if materias_pendientes_cuatrimestre:
                        # Verificar seriación para cada materia
                        materias_a_cursar = []
                        for id_materia in materias_pendientes_cuatrimestre:
                            if self.verificar_prerequisitos(id_materia, simulacion_aprobadas):
                                materias_a_cursar.append(id_materia)
                        
                        # Simular horario con todas estas materias
                        if materias_a_cursar:
                            carga_cuatrimestre = self.simular_planificacion_cuatrimestre(
                                estudiante_simulado, 
                                materias_a_cursar, 
                                cuatrimestre_planificacion
                            )
                            
                            # Añadir al plan completo
                            plan_completo["plan_por_cuatrimestre"][cuatrimestre_planificacion] = carga_cuatrimestre
                            
                            # Actualizar materias "aprobadas" para la simulación
                            for materia_inscrita in carga_cuatrimestre["materias_inscritas"]:
                                id_materia = materia_inscrita["id_materia"]
                                simulacion_aprobadas.add(id_materia)
                                
                                # Actualizar inscripciones simuladas
                                estudiante_simulado.inscripciones_simuladas.append(id_materia)
                                
                                # Eliminar de pendientes
                                for cuatri in list(materias_pendientes_por_cuatrimestre.keys()):
                                    if id_materia in materias_pendientes_por_cuatrimestre[cuatri]:
                                        materias_pendientes_por_cuatrimestre[cuatri].remove(id_materia)
                                        total_materias_pendientes -= 1
                        else:
                            plan_completo["plan_por_cuatrimestre"][cuatrimestre_planificacion] = {
                                "cuatrimestre": cuatrimestre_planificacion,
                                "materias_inscritas": [],
                                "creditos_totales": 0,
                                "num_materias": 0,
                                "advertencia": "No hay materias disponibles para este cuatrimestre debido a seriaciones"
                            }
                    else:
                        plan_completo["plan_por_cuatrimestre"][cuatrimestre_planificacion] = {
                            "cuatrimestre": cuatrimestre_planificacion,
                            "materias_inscritas": [],
                            "creditos_totales": 0,
                            "num_materias": 0,
                            "advertencia": "No hay materias pendientes para este cuatrimestre"
                        }
                else:
                    # Para irregulares, seguimos con la lógica original más flexible
                    # Obtener materias disponibles con restricciones
                    materias_disponibles = []
                    for id_materia, materia in self.materias.items():
                        # No considerar materias ya aprobadas en simulación
                        if id_materia in simulacion_aprobadas:
                            continue
                        
                        # No considerar materias de cuatrimestres futuros
                        if materia.cuatrimestre > cuatrimestre_planificacion:
                            continue
                        
                        # Verificar seriación y prerrequisitos
                        if self.verificar_prerequisitos(id_materia, simulacion_aprobadas):
                            materias_disponibles.append(id_materia)
                    
                    if materias_disponibles:
                        # Priorizar materias para irregulares
                        materias_priorizadas = self.priorizar_materias(
                            materias_disponibles, estudiante_simulado, cuatrimestre_planificacion
                        )
                        
                        # Limitar a 5 materias para irregulares
                        materias_a_cursar = materias_priorizadas[:5]
                        
                        # Simular la planificación
                        carga_cuatrimestre = self.simular_planificacion_cuatrimestre(
                            estudiante_simulado, 
                            materias_a_cursar, 
                            cuatrimestre_planificacion
                        )
                        
                        # Añadir al plan completo
                        if carga_cuatrimestre and carga_cuatrimestre.get("materias_inscritas"):
                            plan_completo["plan_por_cuatrimestre"][cuatrimestre_planificacion] = carga_cuatrimestre
                            
                            # Actualizar materias "aprobadas" para la simulación
                            for materia_inscrita in carga_cuatrimestre["materias_inscritas"]:
                                id_materia = materia_inscrita["id_materia"]
                                simulacion_aprobadas.add(id_materia)
                                
                                # Actualizar inscripciones simuladas
                                estudiante_simulado.inscripciones_simuladas.append(id_materia)
                                
                                # Eliminar de pendientes
                                for cuatri in list(materias_pendientes_por_cuatrimestre.keys()):
                                    if id_materia in materias_pendientes_por_cuatrimestre[cuatri]:
                                        materias_pendientes_por_cuatrimestre[cuatri].remove(id_materia)
                                        total_materias_pendientes -= 1
                        else:
                            plan_completo["plan_por_cuatrimestre"][cuatrimestre_planificacion] = {
                                "cuatrimestre": cuatrimestre_planificacion,
                                "materias_inscritas": [],
                                "creditos_totales": 0,
                                "num_materias": 0,
                                "advertencia": "No se pudieron planificar materias para este cuatrimestre"
                            }
                    else:
                        plan_completo["plan_por_cuatrimestre"][cuatrimestre_planificacion] = {
                            "cuatrimestre": cuatrimestre_planificacion,
                            "materias_inscritas": [],
                            "creditos_totales": 0,
                            "num_materias": 0,
                            "advertencia": "No hay materias disponibles para este cuatrimestre"
                        }
                
                # Limpiar listas vacías de materias pendientes
                materias_pendientes_por_cuatrimestre = {
                    c: materias for c, materias in materias_pendientes_por_cuatrimestre.items() 
                    if materias
                }
                
                # Avanzar al siguiente cuatrimestre
                cuatrimestre_planificacion += 1
            
            # Verificar si alcanzamos el máximo de ciclos (posible ciclo infinito)
            if ciclo_actual >= max_ciclos:
                plan_completo["advertencia"] = "Se alcanzó el máximo de iteraciones en la planificación"
            
            # Actualizar estadísticas finales
            plan_completo["cuatrimestres_restantes"] = len(plan_completo["plan_por_cuatrimestre"])
            plan_completo["fecha_estimada_graduacion"] = self.calcular_fecha_graduacion(cuatrimestre_actual, plan_completo["cuatrimestres_restantes"])
            plan_completo["estadisticas"]["materias_pendientes"] = total_materias_pendientes
            plan_completo["estadisticas"]["porcentaje_avance"] = round(len(materias_aprobadas) / max(1, (len(materias_aprobadas) + total_materias_pendientes)) * 100, 2)
            
            return plan_completo
        except Exception as e:
            import traceback
            print(f"Error en planificar_trayectoria_completa: {e}")
            print(traceback.format_exc())
            
            # Retornar un plan básico con información del error
            return {
                "error": f"Error al planificar trayectoria: {str(e)}",
                "cuatrimestres_restantes": 0,
                "total_materias_pendientes": 0,
                "plan_por_cuatrimestre": {},
                "estadisticas": {
                    "materias_aprobadas": 0,
                    "materias_pendientes": 0,
                    "porcentaje_avance": 0
                }
            }
        
    def optimizar_carga_academica(self, estudiante, tamano_poblacion=100, num_generaciones=30, 
                         tasa_cruce=0.8, tasa_mutacion=0.2, grupos_disponibles=None):
        """Ejecuta el algoritmo genético para optimizar la carga académica."""
        # Verificar estudiante válido
        if not estudiante:
            print("Error: Estudiante no válido para optimización")
            return []
        
        # Determinar materias disponibles
        materias_disponibles = grupos_disponibles or self.get_materias_disponibles(estudiante)
        if not materias_disponibles:
            print("Advertencia: No hay materias disponibles para el estudiante")
            return []
        
        # Verificar si hay materias de estadía entre las disponibles
        estadias = [id_materia for id_materia in materias_disponibles 
                if self.materias.get(id_materia) and self.materias[id_materia].tipo == "Estadía"]
        
        # Si hay estadías disponibles, y el estudiante cumple requisitos, priorizar esas materias
        if estadias:
            print(f"Materias de estadía disponibles: {estadias}")
            # Cuando una estadía está disponible, es la única materia que debe cursarse
            mejor_horario = []
            
            # Obtener todos los grupos de la estadía
            for id_estadia in estadias:
                grupos_estadia = self.materia_a_grupos.get(id_estadia, [])
                
                # Si hay grupos disponibles, elegir uno (el que tenga menor ocupación)
                if grupos_estadia:
                    # Ordenar por menor ocupación (cupo_actual)
                    grupos_ordenados = sorted(grupos_estadia, 
                                            key=lambda id_grupo: self.grupos[id_grupo].cupo_actual 
                                            if id_grupo in self.grupos else float('inf'))
                    
                    for id_grupo in grupos_ordenados:
                        if id_grupo in self.grupos and self.grupos[id_grupo].tiene_cupo():
                            mejor_horario = [id_grupo]
                            break
            
            # Si se encontró un grupo de estadía, retornar ese horario
            if mejor_horario:
                print(f"Se priorizó materia de estadía. Horario: {mejor_horario}")
                return mejor_horario
        
        # Si no hay estadías o no se pudo asignar, continuar con el algoritmo genético normal
        
        # Determinar si usar grupos específicos o generar basados en materias disponibles
        if grupos_disponibles is None:
            if not materias_disponibles:
                print("Advertencia: No hay materias disponibles para el estudiante")
                return []
                
            # Generar población inicial basada en materias disponibles para el estudiante
            poblacion = self.generar_poblacion_inicial(estudiante, tamano_poblacion)
        else:
            # Verificar que grupos_disponibles no esté vacío
            if not grupos_disponibles:
                print("Advertencia: No hay grupos disponibles para optimizar")
                return []
                
            # Generar población inicial basada en grupos específicos
            poblacion = self.generar_poblacion_inicial_con_grupos(
                estudiante, tamano_poblacion, grupos_disponibles
            )
        
        # Si no se pudo generar población, retornar horario vacío
        if not poblacion:
            print("Error: No se pudo generar población inicial")
            return []
        
        # Si todos los individuos en la población están vacíos, retornar lista vacía
        if all(len(individuo) == 0 for individuo in poblacion):
            print("Advertencia: Todos los individuos en la población inicial están vacíos")
            return []
        
        mejor_horario = None
        mejor_fitness = 0
        
        # Ejecutar el algoritmo genético por un número limitado de generaciones
        for generacion in range(num_generaciones):
            # Verificar que la población no esté vacía
            if not poblacion:
                print(f"Advertencia: Población vacía en generación {generacion}")
                break
                
            # Calcular fitness para cada individuo
            fitness = [self.calcular_fitness(estudiante, horario) for horario in poblacion]
            
            # Verificar que haya valores de fitness válidos
            if not fitness or all(f == 0 for f in fitness):
                print(f"Advertencia: No hay individuos con fitness válido en generación {generacion}")
                if generacion == 0:  # Si es la primera generación, no hay solución posible
                    return []
                else:  # Si ya tenemos un mejor horario, lo devolvemos
                    break
            
            # Encontrar el mejor de esta generación
            if fitness:
                idx_mejor = fitness.index(max(fitness))
                if fitness[idx_mejor] > mejor_fitness:
                    mejor_fitness = fitness[idx_mejor]
                    mejor_horario = poblacion[idx_mejor].copy()
            
            # Seleccionar padres (con protección contra población vacía)
            num_padres = max(2, min(tamano_poblacion // 2, len(poblacion)))
            padres = self.seleccionar_padres(poblacion, fitness, num_padres)
            
            # Verificar que haya padres seleccionados
            if not padres:
                print(f"Advertencia: No se seleccionaron padres en generación {generacion}")
                break
            
            # Crear nueva generación
            nueva_poblacion = []
            
            # Elitismo: mantener al mejor
            if mejor_horario:
                nueva_poblacion.append(mejor_horario)
            
            # Cruzar y mutar
            intentos = 0
            max_intentos = tamano_poblacion * 2
            
            while len(nueva_poblacion) < tamano_poblacion and intentos < max_intentos:
                intentos += 1
                
                if len(padres) >= 2:
                    # Asegurarse de elegir padres diferentes
                    indices = list(range(len(padres)))
                    if len(indices) >= 2:
                        idx1, idx2 = random.sample(indices, 2)
                        padre1, padre2 = padres[idx1], padres[idx2]
                    else:
                        # Si solo hay un padre, usarlo dos veces
                        padre1 = padre2 = padres[0]
                    
                    # Probabilidad de cruce
                    if random.random() < tasa_cruce and len(padre1) > 1 and len(padre2) > 1:
                        try:
                            hijo1, hijo2 = self.cruzar(padre1, padre2)
                        except Exception as e:
                            print(f"Error en cruce: {e} - Usando padres directamente")
                            hijo1, hijo2 = padre1.copy(), padre2.copy()
                    else:
                        hijo1, hijo2 = padre1.copy(), padre2.copy()
                    
                    # Mutación
                    try:
                        hijo1 = self.mutar(hijo1, tasa_mutacion, estudiante, grupos_disponibles)
                        hijo2 = self.mutar(hijo2, tasa_mutacion, estudiante, grupos_disponibles)
                    except Exception as e:
                        print(f"Error en mutación: {e}")
                    
                    nueva_poblacion.append(hijo1)
                    if len(nueva_poblacion) < tamano_poblacion:
                        nueva_poblacion.append(hijo2)
                else:
                    # Si no hay suficientes padres, duplicar los existentes
                    nueva_poblacion.extend(padres)
                    break
            
            # Verificar que la nueva población no esté vacía
            if not nueva_poblacion:
                print(f"Advertencia: Nueva población vacía en generación {generacion}")
                break
                
            # Actualizar población
            poblacion = nueva_poblacion
        
        return mejor_horario or []
    
    def planificar_cuatrimestre(self, estudiante, materias_disponibles, num_cuatrimestre):
        """Planifica la carga óptima para un cuatrimestre específico."""
        # Verificar que haya materias disponibles
        if not materias_disponibles:
            print(f"Advertencia: No hay materias disponibles para el cuatrimestre {num_cuatrimestre}")
            return {
                "cuatrimestre": num_cuatrimestre,
                "materias_inscritas": [],
                "creditos_totales": 0,
                "num_materias": 0,
                "horario_semanal": {},
                "carga_por_dia": {dia: 0 for dia in range(1, 6)},
                "advertencia": "No hay materias disponibles para este cuatrimestre"
            }
        
        # Primero filtramos las materias por prioridad
        materias_priorizadas = self.priorizar_materias(materias_disponibles, estudiante, num_cuatrimestre)
        
        # Creamos un estudiante simulado para este cuatrimestre si es en el futuro
        estudiante_simulado = estudiante
        if num_cuatrimestre > estudiante.cuatrimestre:
            import copy
            estudiante_simulado = copy.deepcopy(estudiante)
            estudiante_simulado.cuatrimestre = num_cuatrimestre
        
        # Obtener grupos disponibles para estas materias
        grupos_disponibles = []
        for id_materia in materias_priorizadas:
            if id_materia in self.materia_a_grupos:
                for id_grupo in self.materia_a_grupos[id_materia]:
                    grupos_disponibles.append(id_grupo)
        
        # Verificar que haya grupos disponibles
        if not grupos_disponibles:
            print(f"Advertencia: No hay grupos disponibles para las materias del cuatrimestre {num_cuatrimestre}")
            return {
                "cuatrimestre": num_cuatrimestre,
                "materias_inscritas": [],
                "creditos_totales": 0,
                "num_materias": 0,
                "horario_semanal": {},
                "carga_por_dia": {dia: 0 for dia in range(1, 6)},
                "advertencia": "No hay grupos disponibles para las materias de este cuatrimestre"
            }
        
        # Usar algoritmo genético para optimizar esta carga
        mejor_horario = self.optimizar_carga_academica(
            estudiante_simulado,
            tamano_poblacion=100,
            num_generaciones=30,
            tasa_cruce=0.8,
            tasa_mutacion=0.2,
            grupos_disponibles=grupos_disponibles
        )
        
        # Si no se encontró un horario válido o el horario está vacío
        if not mejor_horario:
            return {
                "cuatrimestre": num_cuatrimestre,
                "materias_inscritas": [],
                "creditos_totales": 0,
                "num_materias": 0,
                "horario_semanal": {},
                "carga_por_dia": {dia: 0 for dia in range(1, 6)},
                "advertencia": "No se pudo generar un horario válido para este cuatrimestre"
            }
        
        # Generar visualización del horario
        horario_semanal = self.generar_horario_semanal(mejor_horario)
        
        # Obtener información detallada
        materias_inscritas = []
        creditos_totales = 0
        
        for id_grupo in mejor_horario:
            grupo = self.grupos.get(id_grupo)
            if grupo:
                materia = self.materias.get(grupo.id_materia)
                if materia:
                    materias_inscritas.append({
                        "id_materia": materia.id,
                        "nombre_materia": materia.nombre,
                        "id_grupo": grupo.id,
                        "profesor": grupo.profesor,
                        "creditos": materia.creditos,
                        "cuatrimestre": materia.cuatrimestre,
                        "tipo": materia.tipo,
                        "horarios": grupo.horarios
                    })
                    creditos_totales += materia.creditos
        
        # Calcular distribución por día
        carga_por_dia = {}
        for dia in range(1, 6):  # Lunes a Viernes
            carga_por_dia[dia] = 0
        
        for id_grupo in mejor_horario:
            grupo = self.grupos.get(id_grupo)
            if grupo and hasattr(grupo, 'horarios') and grupo.horarios:
                for dia, _, _, _ in grupo.horarios:
                    if 1 <= dia <= 5:  # Solo días hábiles
                        carga_por_dia[dia] += 1
        
        return {
            "cuatrimestre": num_cuatrimestre,
            "materias_inscritas": materias_inscritas,
            "creditos_totales": creditos_totales,
            "num_materias": len(materias_inscritas),
            "horario_semanal": horario_semanal,
            "carga_por_dia": carga_por_dia
        }
    
    def priorizar_materias(self, materias_disponibles, estudiante, num_cuatrimestre):
        """Prioriza las materias disponibles según diversos criterios.
        
        Args:
            materias_disponibles (list): Lista de IDs de materias disponibles.
            estudiante (Estudiante): Objeto estudiante.
            num_cuatrimestre (int): Número de cuatrimestre actual.
            
        Returns:
            list: Lista ordenada de materias priorizadas.
        """
        # Calcular puntaje de prioridad para cada materia
        materias_puntaje = []
        
        for id_materia in materias_disponibles:
            materia = self.materias.get(id_materia)
            if not materia:
                continue
                
            # Criterios de priorización
            puntaje = 0
            
            # 1. Materias de cuatrimestres anteriores tienen mayor prioridad
            diferencia_cuatri = num_cuatrimestre - materia.cuatrimestre
            if diferencia_cuatri > 0:
                puntaje += diferencia_cuatri * 10  # Alta prioridad a materias atrasadas
            
            # 2. Materias que son prerrequisito de muchas otras
            dependientes = 0
            for id_materia_dep, prereqs in self.seriacion.items():
                if id_materia in prereqs:
                    dependientes += 1
            puntaje += dependientes * 5
            
            # 3. Proyectos integradores y Estadías tienen alta prioridad
            if materia.tipo == "Proyecto Integrador":
                puntaje += 15
            elif materia.tipo == "Estadía":
                puntaje += 20
            
            # 4. Priorizar materias del mismo cuatrimestre
            if materia.cuatrimestre == num_cuatrimestre:
                puntaje += 3
            
            materias_puntaje.append((id_materia, puntaje))
        
        # Ordenar por puntaje descendente
        materias_puntaje.sort(key=lambda x: x[1], reverse=True)
        
        # Devolver solo los IDs de materias ordenados
        return [id_materia for id_materia, _ in materias_puntaje]
    

    
    def mutar(self, horario, tasa_mutacion, estudiante, grupos_disponibles=None):
        """Aplica mutación a un horario con posible limitación de grupos."""
        if not horario or random.random() > tasa_mutacion:
            return horario
        
        # Elegir grupo a mutar
        idx_mutar = random.randint(0, len(horario) - 1)
        id_grupo_actual = horario[idx_mutar]
        id_materia_actual = self.grupos[id_grupo_actual].id_materia
        
        # Determinar grupos disponibles para esta materia
        if grupos_disponibles:
            grupos_para_materia = [
                id_grupo for id_grupo in grupos_disponibles 
                if self.grupos.get(id_grupo) and self.grupos[id_grupo].id_materia == id_materia_actual
            ]
        else:
            grupos_para_materia = self.materia_a_grupos.get(id_materia_actual, [])
        
        # Intentar reemplazar por otro grupo de la misma materia
        otros_grupos = [id_grupo for id_grupo in grupos_para_materia if id_grupo != id_grupo_actual]
        
        if otros_grupos:
            nuevo_grupo = random.choice(otros_grupos)
            
            # Verificar conflictos de horario
            conflicto = False
            for id_grupo in horario:
                if id_grupo != id_grupo_actual and self.hay_conflicto_horario(
                    self.grupos[nuevo_grupo].horarios, self.grupos[id_grupo].horarios):
                    conflicto = True
                    break
            
            if not conflicto:
                horario_mutado = horario.copy()
                horario_mutado[idx_mutar] = nuevo_grupo
                return horario_mutado
        
        # Si no podemos mutar el grupo, intentar reemplazar la materia
        if grupos_disponibles:
            # Materias disponibles a través de los grupos disponibles
            materias_disponibles = set()
            for id_grupo in grupos_disponibles:
                grupo = self.grupos.get(id_grupo)
                if grupo:
                    materias_disponibles.add(grupo.id_materia)
        else:
            materias_disponibles = self.get_materias_disponibles(estudiante)
        
        materias_actuales = {self.grupos[id_grupo].id_materia for id_grupo in horario}
        nuevas_materias = [m for m in materias_disponibles if m not in materias_actuales]
        
        if nuevas_materias:
            nueva_materia = random.choice(nuevas_materias)
            
            if grupos_disponibles:
                grupos_nuevos = [
                    id_grupo for id_grupo in grupos_disponibles
                    if self.grupos.get(id_grupo) and self.grupos[id_grupo].id_materia == nueva_materia
                ]
            else:
                grupos_nuevos = self.materia_a_grupos.get(nueva_materia, [])
            
            if grupos_nuevos:
                random.shuffle(grupos_nuevos)
                for nuevo_grupo in grupos_nuevos:
                    # Verificar cupo
                    if not self.grupos[nuevo_grupo].tiene_cupo():
                        continue
                    
                    # Verificar conflictos de horario
                    conflicto = False
                    for id_grupo in horario:
                        if id_grupo != id_grupo_actual and self.hay_conflicto_horario(
                            self.grupos[nuevo_grupo].horarios, self.grupos[id_grupo].horarios):
                            conflicto = True
                            break
                    
                    if not conflicto:
                        horario_mutado = horario.copy()
                        horario_mutado[idx_mutar] = nuevo_grupo
                        return horario_mutado
        
        return horario
    
    def calcular_fecha_graduacion(self, cuatrimestre_actual, cuatrimestres_restantes):
        """Calcula la fecha estimada de graduación.
        
        Args:
            cuatrimestre_actual (int): Cuatrimestre actual del estudiante.
            cuatrimestres_restantes (int): Número de cuatrimestres restantes.
            
        Returns:
            str: Fecha estimada en formato "Mes Año".
        """
        import datetime
        
        # Obtener fecha actual
        ahora = datetime.datetime.now()
        
        # Determinar el cuatrimestre actual por la fecha del año
        mes_actual = ahora.month
        
        # En un sistema típico de 3 cuatrimestres por año:
        # Cuatrimestre 1: Enero-Abril
        # Cuatrimestre 2: Mayo-Agosto
        # Cuatrimestre 3: Septiembre-Diciembre
        if 1 <= mes_actual <= 4:
            cuatri_calendario = 1
        elif 5 <= mes_actual <= 8:
            cuatri_calendario = 2
        else:
            cuatri_calendario = 3
        
        # Calcular cuántos cuatrimestres totales desde ahora
        total_cuatrimestres = cuatrimestres_restantes
        
        # Calcular años y cuatrimestres adicionales
        anos_adicionales = total_cuatrimestres // 3
        cuatrimestres_adicionales = total_cuatrimestres % 3
        
        # Calcular nuevo cuatrimestre de calendario
        nuevo_cuatri_calendario = (cuatri_calendario + cuatrimestres_adicionales) % 3
        if nuevo_cuatri_calendario == 0:
            nuevo_cuatri_calendario = 3
        
        # Ajustar si pasamos al siguiente año
        if cuatri_calendario + cuatrimestres_adicionales > 3:
            anos_adicionales += 1
        
        # Calcular nueva fecha
        nuevo_ano = ahora.year + anos_adicionales
        
        # Determinar mes de graduación basado en el cuatrimestre de calendario
        if nuevo_cuatri_calendario == 1:
            mes_graduacion = "Abril"
        elif nuevo_cuatri_calendario == 2:
            mes_graduacion = "Agosto"
        else:
            mes_graduacion = "Diciembre"
        
        return f"{mes_graduacion} {nuevo_ano}"