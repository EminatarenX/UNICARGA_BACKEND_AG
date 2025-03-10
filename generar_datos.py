import csv
import random
import os

def crear_carpeta_datos(carpeta="data"):
    """Crea la carpeta donde se guardarán los archivos CSV."""
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)
    return carpeta

def generar_materias(carpeta):
    """Genera materias.csv con el plan completo de 10 cuatrimestres."""
    
    # Horas correctas por materia según el documento
    horas_por_materia = {
        # Primer cuatrimestre
        1: 75,   # INGLÉS I
        2: 60,   # DESARROLLO HUMANO Y VALORES
        3: 105,  # FUNDAMENTOS MATEMÁTICOS
        4: 90,   # FUNDAMENTOS DE REDES
        5: 90,   # FÍSICA
        6: 60,   # FUNDAMENTOS DE PROGRAMACIÓN
        7: 75,   # COMUNICACIÓN Y HABILIDADES DIGITALES
        
        # Segundo cuatrimestre
        8: 75,   # INGLÉS II
        9: 60,   # HABILIDADES SOCIOEMOCIONALES Y MANEJO DE CONFLICTOS
        10: 90,  # CÁLCULO DIFERENCIAL
        11: 75,  # CONMUTACIÓN Y ENRUTAMIENTO DE REDES
        12: 75,  # PROBABILIDAD Y ESTADÍSTICA
        13: 75,  # PROGRAMACIÓN ESTRUCTURADA
        14: 75,  # SISTEMAS OPERATIVOS
        
        # Tercer cuatrimestre
        15: 75,  # INGLÉS III
        16: 60,  # DESARROLLO DEL PENSAMIENTO Y TOMA DE DECISIONES
        17: 60,  # CÁLCULO INTEGRAL
        18: 90,  # TÓPICOS DE CALIDAD PARA EL DISEÑO DE SOFTWARE
        19: 75,  # BASES DE DATOS
        20: 105, # PROGRAMACIÓN ORIENTADA A OBJETOS
        21: 60,  # PROYECTO INTEGRADOR I
        
        # Cuarto cuatrimestre
        22: 75,  # INGLÉS IV
        23: 60,  # ÉTICA PROFESIONAL
        24: 75,  # CÁLCULO DE VARIAS VARIABLES
        25: 75,  # APLICACIONES WEB
        26: 75,  # ESTRUCTURA DE DATOS
        27: 90,  # DESARROLLO DE APLICACIONES MÓVILES
        28: 75,  # ANÁLISIS Y DISEÑO DE SOFTWARE
        
        # Quinto cuatrimestre
        29: 75,  # INGLÉS V
        30: 60,  # LIDERAZGO DE EQUIPOS DE ALTO DESEMPEÑO
        31: 75,  # ECUACIONES DIFERENCIALES
        32: 90,  # APLICACIONES WEB ORIENTADAS A SERVICIOS
        33: 75,  # BASES DE DATOS AVANZADAS
        34: 90,  # ESTÁNDARES Y MÉTRICAS PARA EL DESARROLLO DE SOFTWARE
        35: 60,  # PROYECTO INTEGRADOR II
        
        # Sexto cuatrimestre
        36: 600, # ESTADÍA I
        
        # Séptimo cuatrimestre
        37: 75,  # INGLÉS VI
        38: 60,  # HABILIDADES GERENCIALES
        39: 60,  # FORMULACIÓN DE PROYECTOS DE TECNOLOGÍA
        40: 90,  # FUNDAMENTOS DE INTELIGENCIA ARTIFICIAL
        41: 60,  # ÉTICA Y LEGISLACIÓN EN TECNOLOGÍAS DE LA INFORMACIÓN
        42: 90,  # OPTATIVA I
        43: 90,  # SEGURIDAD INFORMÁTICA
        
        # Octavo cuatrimestre
        44: 75,  # INGLÉS VII
        45: 75,  # ELECTRÓNICA DIGITAL
        46: 90,  # GESTIÓN DE PROYECTOS DE TECNOLOGÍA
        47: 75,  # PROGRAMACIÓN PARA INTELIGENCIA ARTIFICIAL
        48: 75,  # ADMINISTRACIÓN DE SERVIDORES
        49: 90,  # OPTATIVA II
        50: 75,  # INFORMÁTICA FORENSE
        
        # Noveno cuatrimestre
        51: 75,  # INGLÉS VIII
        52: 75,  # INTERNET DE LAS COSAS
        53: 90,  # EVALUACIÓN DE PROYECTOS DE TECNOLOGÍA
        54: 90,  # CIENCIA DE DATOS
        55: 75,  # TECNOLOGÍAS DISRUPTIVAS
        56: 90,  # OPTATIVA III
        57: 60,  # PROYECTO INTEGRADOR III
        
        # Décimo cuatrimestre
        58: 600  # ESTADÍA II
    }
    
    # Definir créditos y horas totales por cuatrimestre
    info_cuatrimestre = {
        1: {"creditos": 32.81, "horas": 525},  # Primer cuatrimestre
        2: {"creditos": 32.81, "horas": 525},  # Segundo cuatrimestre
        3: {"creditos": 32.81, "horas": 525},  # Tercer cuatrimestre
        4: {"creditos": 32.81, "horas": 525},  # Cuarto cuatrimestre
        5: {"creditos": 32.81, "horas": 525},  # Quinto cuatrimestre
        6: {"creditos": 37.50, "horas": 600},  # Sexto cuatrimestre (Estadía)
        7: {"creditos": 32.81, "horas": 525},  # Séptimo cuatrimestre
        8: {"creditos": 32.81, "horas": 525},  # Octavo cuatrimestre
        9: {"creditos": 32.81, "horas": 525},  # Noveno cuatrimestre
        10: {"creditos": 37.50, "horas": 600}   # Décimo cuatrimestre (Estadía)
    }
    
    # Configuración base de materias (mantener nombres y tipos, actualizar horas y créditos)
    materias_base = [
        # 1er cuatrimestre
        (1, "Inglés I", 1, None, None, "Regular"),
        (2, "Desarrollo humano y valores", 1, None, None, "Regular"),
        (3, "Fundamentos matemáticos", 1, None, None, "Regular"),
        (4, "Fundamentos de redes", 1, None, None, "Regular"),
        (5, "Física", 1, None, None, "Regular"),
        (6, "Fundamentos de programación", 1, None, None, "Regular"),
        (7, "Comunicación y habilidades digitales", 1, None, None, "Regular"),
        
        # 2do cuatrimestre
        (8, "Inglés II", 2, None, None, "Regular"),
        (9, "Habilidades socioemocionales y manejo de conflictos", 2, None, None, "Regular"),
        (10, "Cálculo diferencial", 2, None, None, "Regular"),
        (11, "Conmutación y enrutamiento de redes", 2, None, None, "Regular"),
        (12, "Probabilidad y estadística", 2, None, None, "Regular"),
        (13, "Programación estructurada", 2, None, None, "Regular"),
        (14, "Sistemas operativos", 2, None, None, "Regular"),
        
        # 3er cuatrimestre
        (15, "Inglés III", 3, None, None, "Regular"),
        (16, "Desarrollo del pensamiento y toma de decisiones", 3, None, None, "Regular"),
        (17, "Cálculo integral", 3, None, None, "Regular"),
        (18, "Tópicos de calidad para el diseño de software", 3, None, None, "Regular"),
        (19, "Bases de datos", 3, None, None, "Regular"),
        (20, "Programación orientada a objetos", 3, None, None, "Regular"),
        (21, "Proyecto integrador I", 3, None, None, "Proyecto Integrador"),
        
        # 4to cuatrimestre
        (22, "Inglés IV", 4, None, None, "Regular"),
        (23, "Ética profesional", 4, None, None, "Regular"),
        (24, "Cálculo de varias variables", 4, None, None, "Regular"),
        (25, "Aplicaciones web", 4, None, None, "Regular"),
        (26, "Estructura de datos", 4, None, None, "Regular"),
        (27, "Desarrollo de aplicaciones móviles", 4, None, None, "Regular"),
        (28, "Análisis y diseño de software", 4, None, None, "Regular"),
        
        # 5to cuatrimestre
        (29, "Inglés V", 5, None, None, "Regular"),
        (30, "Liderazgo de equipos de alto desempeño", 5, None, None, "Regular"),
        (31, "Ecuaciones diferenciales", 5, None, None, "Regular"),
        (32, "Aplicaciones web orientadas a servicios", 5, None, None, "Regular"),
        (33, "Bases de datos avanzadas", 5, None, None, "Regular"),
        (34, "Estándares y métricas para el desarrollo de software", 5, None, None, "Regular"),
        (35, "Proyecto integrador II", 5, None, None, "Proyecto Integrador"),
        
        # 6to cuatrimestre - Estadía
        (36, "Estadía I", 6, None, None, "Estadía"),
        
        # 7mo cuatrimestre
        (37, "Inglés VI", 7, None, None, "Regular"),
        (38, "Habilidades gerenciales", 7, None, None, "Regular"),
        (39, "Formulación de proyectos de tecnología", 7, None, None, "Regular"),
        (40, "Fundamentos de inteligencia artificial", 7, None, None, "Regular"),
        (41, "Ética y legislación en tecnologías de la información", 7, None, None, "Regular"),
        (42, "Optativa I", 7, None, None, "Regular"),
        (43, "Seguridad informática", 7, None, None, "Regular"),
        
        # 8vo cuatrimestre
        (44, "Inglés VII", 8, None, None, "Regular"),
        (45, "Electrónica digital", 8, None, None, "Regular"),
        (46, "Gestión de proyectos de tecnología", 8, None, None, "Regular"),
        (47, "Programación para inteligencia artificial", 8, None, None, "Regular"),
        (48, "Administración de servidores", 8, None, None, "Regular"),
        (49, "Optativa II", 8, None, None, "Regular"),
        (50, "Informática forense", 8, None, None, "Regular"),
        
        # 9no cuatrimestre
        (51, "Inglés VIII", 9, None, None, "Regular"),
        (52, "Internet de las cosas", 9, None, None, "Regular"),
        (53, "Evaluación de proyectos de tecnología", 9, None, None, "Regular"),
        (54, "Ciencia de datos", 9, None, None, "Regular"),
        (55, "Tecnologías disruptivas", 9, None, None, "Regular"),
        (56, "Optativa III", 9, None, None, "Regular"),
        (57, "Proyecto integrador III", 9, None, None, "Proyecto Integrador"),
        
        # 10mo cuatrimestre - Estadía
        (58, "Estadía II", 10, None, None, "Estadía")
    ]
    
    # Actualizar materias con horas correctas y calcular créditos
    materias = []
    
    # Para calcular créditos de manera precisa, primero obtengamos las horas totales por cuatrimestre
    horas_reales_por_cuatrimestre = {}
    for id_materia, _, cuatrimestre, _, _, _ in materias_base:
        if cuatrimestre not in horas_reales_por_cuatrimestre:
            horas_reales_por_cuatrimestre[cuatrimestre] = 0
        horas_reales_por_cuatrimestre[cuatrimestre] += horas_por_materia.get(id_materia, 75)
    
    # Ahora creamos las materias con valores actualizados
    for id_materia, nombre, cuatrimestre, _, _, tipo in materias_base:
        # Obtener horas correctas
        horas = horas_por_materia.get(id_materia, 75)
        
        # Calcular créditos proporcionales usando la proporción real
        if cuatrimestre in info_cuatrimestre:
            # Proporción = (horas_materia / horas_reales_cuatrimestre) * creditos_totales_cuatrimestre
            horas_cuatri = horas_reales_por_cuatrimestre[cuatrimestre]
            creditos_cuatri = info_cuatrimestre[cuatrimestre]["creditos"]
            
            if horas_cuatri > 0:
                creditos = (horas / horas_cuatri) * creditos_cuatri
                creditos = round(creditos, 2)  # Redondear a 2 decimales
            else:
                creditos = creditos_cuatri  # Caso especial para estadías
        else:
            # Valor por defecto si no hay información del cuatrimestre
            creditos = 5.0
        
        # Para estadías, usar directamente los créditos totales
        if tipo == "Estadía":
            creditos = info_cuatrimestre[cuatrimestre]["creditos"]
        
        materias.append((id_materia, nombre, cuatrimestre, creditos, horas, tipo))
    
    # Escribir al archivo CSV
    with open(os.path.join(carpeta, "materias.csv"), 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["id_materia", "nombre", "cuatrimestre", "creditos", "horas_totales", "tipo"])
        writer.writerows(materias)
    
    return materias


def generar_seriacion(carpeta):
    """Genera seriacion.csv con las dependencias completas."""
    seriacion = [
        # Inglés
        (8, 1),    # Inglés II requiere Inglés I
        (15, 8),   # Inglés III requiere Inglés II
        (22, 15),  # Inglés IV requiere Inglés III
        (29, 22),  # Inglés V requiere Inglés IV
        (37, 29),  # Inglés VI requiere Inglés V
        (44, 37),  # Inglés VII requiere Inglés VI
        (51, 44),  # Inglés VIII requiere Inglés VII
        
        # Desarrollo humano
        (9, 2),    # Habilidades socioemocionales requiere Desarrollo humano
        (16, 9),   # Desarrollo del pensamiento requiere Habilidades socioemocionales
        (23, 16),  # Ética profesional requiere Desarrollo del pensamiento
        (30, 23),  # Liderazgo requiere Ética profesional
        (38, 30),  # Habilidades gerenciales requiere Liderazgo
        
        # Matemáticas
        (10, 3),   # Cálculo diferencial requiere Fundamentos matemáticos
        (17, 10),  # Cálculo integral requiere Cálculo diferencial
        (24, 17),  # Cálculo de varias variables requiere Cálculo integral
        (31, 24),  # Ecuaciones diferenciales requiere Cálculo de varias variables
        
        # Redes
        (11, 4),   # Conmutación y enrutamiento requiere Fundamentos de redes
        (14, 4),   # Sistemas operativos requiere Fundamentos de redes
        (48, 11),  # Administración de servidores requiere Conmutación y enrutamiento
        
        # Programación
        (13, 6),   # Programación estructurada requiere Fundamentos de programación
        (20, 13),  # POO requiere Programación estructurada
        (26, 20),  # Estructura de datos requiere POO
        (27, 20),  # Desarrollo de aplicaciones móviles requiere POO
        (47, 40),  # Programación para IA requiere Fundamentos de IA
        
        # Proyectos de tecnología
        (46, 39),  # Gestión de proyectos requiere Formulación de proyectos
        (53, 46),  # Evaluación de proyectos requiere Gestión de proyectos
        
        # Bases de datos
        (33, 19),  # Bases de datos avanzadas requiere Bases de datos
        (54, 33),  # Ciencia de datos requiere Bases de datos avanzadas
        
        # Desarrollo web
        (32, 25),  # Aplicaciones web orientadas a servicios requiere Aplicaciones web
        
        # Proyectos integradores y Estadías
        (35, 21),  # Proyecto integrador II requiere Proyecto integrador I
        (57, 35),  # Proyecto integrador III requiere Proyecto integrador II
        (36, 35),  # Estadía I requiere Proyecto integrador II
        (58, 57)   # Estadía II requiere Proyecto integrador III
    ]
    
    with open(os.path.join(carpeta, "seriacion.csv"), 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["id_materia", "id_prerequisito"])
        writer.writerows(seriacion)
    
    return seriacion

def generar_dependencias_proyectos(carpeta):
    """Genera dependencias_proyectos.csv para todos los proyectos integradores."""
    dependencias = [
        # Proyecto integrador I (3er cuatrimestre)
        (21, 19),  # Proyecto integrador I depende de Bases de datos
        (21, 18),  # Proyecto integrador I depende de Tópicos de calidad
        (21, 20),  # Proyecto integrador I depende de POO
        
        # Proyecto integrador II (5to cuatrimestre)
        (35, 32),  # Proyecto integrador II depende de Aplicaciones web orientadas a servicios
        (35, 33),  # Proyecto integrador II depende de Bases de datos avanzadas
        (35, 34),  # Proyecto integrador II depende de Estándares y métricas
        
        # Estadía I (6to cuatrimestre)
        (36, 35),  # Estadía I depende de Proyecto integrador II
        # También debe heredar indirectamente las dependencias del Proyecto integrador II
        (36, 32),  # Estadía I depende de Aplicaciones web orientadas a servicios
        (36, 33),  # Estadía I depende de Bases de datos avanzadas
        (36, 34),  # Estadía I depende de Estándares y métricas
        
        # Proyecto integrador III (9no cuatrimestre)
        (57, 47),  # Proyecto integrador III depende de Programación para IA
        (57, 54),  # Proyecto integrador III depende de Ciencia de datos
        (57, 55),  # Proyecto integrador III depende de Tecnologías disruptivas
        
        # Estadía II (10mo cuatrimestre)
        (58, 57)   # Estadía II depende de Proyecto integrador III
    ]
    
    with open(os.path.join(carpeta, "dependencias_proyectos.csv"), 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["id_proyecto", "id_materia_dependiente"])
        writer.writerows(dependencias)
    
    return dependencias

def generar_profesores(num_profesores=15):
    """Genera una lista de profesores aleatorios."""
    nombres = ["Juan", "María", "Pedro", "Ana", "Carlos", "Laura", "José", "Patricia", 
             "Miguel", "Sofía", "Fernando", "Elena", "Javier", "Silvia", "Ricardo"]
    
    apellidos = ["García", "López", "Martínez", "Rodríguez", "González", "Hernández", 
               "Pérez", "Sánchez", "Ramírez", "Torres", "Flores", "Rivera", "Gómez"]
    
    profesores = []
    for i in range(num_profesores):
        nombre = random.choice(nombres)
        apellido1 = random.choice(apellidos)
        apellido2 = random.choice(apellidos)
        titulo = random.choice(["Dr.", "Dra.", "Mtro.", "Mtra.", "Ing.", "Lic."])
        profesores.append(f"{titulo} {nombre} {apellido1} {apellido2}")
    
    return profesores

def generar_grupos_y_horarios(carpeta, materias):
    """Genera grupos.csv y horarios.csv."""
    profesores = generar_profesores(15)
    
    # Preparar datos para grupos
    grupos = []
    horarios = []
    id_grupo = 1
    id_horario = 1
    
    for id_materia, nombre, cuatrimestre, creditos, horas, tipo in materias:
        if tipo == "Estadía":
            continue
        
        # Crear 2-3 grupos por materia
        num_grupos = random.randint(2, 3)
        for i in range(1, num_grupos + 1):
            # Datos del grupo
            profesor = random.choice(profesores)
            
            # Generar cupo con 80% de probabilidad alrededor de 20
            if random.random() < 0.8:
                cupo_maximo = random.randint(18, 22)  # Cupo estándar (cerca de 20)
            else:
                cupo_maximo = random.randint(23, 30)  # Cupo extendido (cargas manuales)
                
            cupo_actual = random.randint(0, cupo_maximo)
            
            grupos.append((id_grupo, id_materia, profesor, cupo_maximo, cupo_actual))
            
            # Crear horarios para este grupo
            dias_semana = [1, 2, 3, 4, 5]  # Lunes a Viernes
            random.shuffle(dias_semana)
            num_sesiones = 2 if horas > 60 else 1
            
            for j in range(num_sesiones):
                dia = dias_semana[j]
                
                # Horarios posibles (ajustados al horario real de la universidad)
                # Principalmente de 8am a 4pm, con algunos casos hasta las 7pm
                if random.random() < 0.85:  # 85% de probabilidad para horarios regulares
                    hora_inicio = random.choice([8, 10, 12, 14, 16])  # Horarios comunes (8am-4pm)
                else:  # 15% de probabilidad para horarios extendidos
                    hora_inicio = random.choice([18, 19])  # Horarios extendidos (6pm-7pm)
                
                hora_fin = hora_inicio + 2  # Clases de 2 horas
                
                aula = f"{random.choice(['A', 'B', 'C'])}{random.randint(101, 310)}"
                
                horarios.append((id_horario, id_grupo, dia, f"{hora_inicio:02d}:00", f"{hora_fin:02d}:00", aula))
                id_horario += 1
            
            id_grupo += 1
    
    # Guardar grupos.csv
    with open(os.path.join(carpeta, "grupos.csv"), 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["id_grupo", "id_materia", "profesor", "cupo_maximo", "cupo_actual"])
        writer.writerows(grupos)
    
    # Guardar horarios.csv
    with open(os.path.join(carpeta, "horarios.csv"), 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["id_horario", "id_grupo", "dia", "hora_inicio", "hora_fin", "aula"])
        writer.writerows(horarios)
    
    return grupos, horarios

def generar_estudiantes(carpeta, num_estudiantes=200):
    """Genera estudiantes.csv."""
    estudiantes = []
    
    nombres = [
        "Juan", "María", "Pedro", "Ana", "Carlos", "Laura", "José", "Patricia", "Miguel", "Sofía",
        "Fernando", "Elena", "Javier", "Silvia", "Ricardo", "Gabriel", "Daniela", "Alejandro", "Valentina", "Jorge",
        "Camila", "Andrés", "Luis", "Adriana", "Antonio", "Isabel", "Francisco", "Lucía", "Raúl", "Marina",
        "Roberto", "Carmen", "Manuel", "Alejandra", "Sergio", "Diana", "Alberto", "Rosa", "Diego", "Claudia",
        "Arturo", "Mónica", "Guadalupe", "Verónica", "Rafael", "Teresa", "Jesús", "Alicia", "Oscar", "Beatriz",
        "Pablo", "Lorena", "Rubén", "Maribel", "Héctor", "Yolanda", "Víctor", "Natalia", "Eduardo", "Angélica",
        "Salvador", "Cecilia", "Felipe", "Leticia", "Alfonso", "Estela", "Joaquín", "Reyna", "Iván", "Maricela",
        "Enrique", "Esperanza", "Gerardo", "Consuelo", "Rodolfo", "Olivia", "César", "Paula", "Hugo", "Noemí",
        "Julio", "Karla", "Ramiro", "Irene", "Emilio", "Miriam", "Mario", "Susana", "Erick", "Magdalena",
        "Leonardo", "Dolores", "Abel", "Ruth", "Gilberto", "Amalia", "Ernesto", "Elsa", "Federico", "Rocío"
    ]
    
    apellidos = [
        "García", "López", "Martínez", "Rodríguez", "González", "Hernández", "Pérez", "Sánchez", "Ramírez", "Torres",
        "Flores", "Rivera", "Gómez", "Vargas", "Castro", "Ortiz", "Ramos", "Romero", "Gutiérrez", "Díaz",
        "Morales", "Ortega", "Reyes", "Cruz", "Medina", "Aguilar", "Vázquez", "Jiménez", "Mendoza", "Ruiz",
        "Salazar", "Alvarado", "Castillo", "Chávez", "Juárez", "Núñez", "Guerrero", "Rojas", "Delgado", "Méndez",
        "Santos", "Cervantes", "Vega", "Cabrera", "Peña", "Ríos", "Mejía", "Soto", "Contreras", "Valdez",
        "Navarro", "Acosta", "Miranda", "Figueroa", "Cortés", "Luna", "Espinoza", "Álvarez", "León", "Molina",
        "Campos", "Herrera", "Pacheco", "Rosas", "Aguirre", "Orozco", "Padilla", "Zamora", "Serrano", "Rangel",
        "Téllez", "Barrera", "Franco", "Gallegos", "Cárdenas", "Velázquez", "Montes", "Soria", "Escobar", "Ibarra",
        "Quintero", "Zúñiga", "Bravo", "Galván", "Osorio", "De La Cruz", "Ponce", "Valencia", "Corona", "Avila"
    ]
    
    for id_estudiante in range(1, num_estudiantes + 1):
        nombre = f"{random.choice(nombres)} {random.choice(apellidos)} {random.choice(apellidos)}"
        cuatrimestre = random.randint(1, 5)
        # Modificar la línea de asignación de estatus:
        status = "Regular" if cuatrimestre == 1 or random.random() < 0.8 else "Irregular"
        
        # Creditos basados en cuatrimestre y status
        if status == "Regular":
            creditos_base = cuatrimestre * 32.81
            creditos_acumulados = round(creditos_base, 2)
        else:
            creditos_base = (cuatrimestre - 1) * 32.81
            factor_creditos = random.uniform(0.7, 0.9)
            creditos_acumulados = round(creditos_base * factor_creditos, 2)
        
        max_creditos = random.randint(30, 36)
        
        estudiantes.append((id_estudiante, nombre, cuatrimestre, status, creditos_acumulados, max_creditos))
    
    with open(os.path.join(carpeta, "estudiantes.csv"), 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["id_estudiante", "nombre", "cuatrimestre_actual", "status", "creditos_acumulados", "max_creditos"])
        writer.writerows(estudiantes)
    
    return estudiantes

def generar_historial_academico(carpeta, estudiantes, materias):
    """Genera historial_academico.csv."""
    historial = []
    
    # Agrupar materias por cuatrimestre
    materias_por_cuatrimestre = {}
    for materia in materias:
        id_materia, nombre, cuatrimestre, creditos, horas, tipo = materia
        if cuatrimestre not in materias_por_cuatrimestre:
            materias_por_cuatrimestre[cuatrimestre] = []
        materias_por_cuatrimestre[cuatrimestre].append(materia)
    
    for id_estudiante, nombre, cuatrimestre_actual, status, creditos_acumulados, max_creditos in estudiantes:
        # Determinar cuatrimestres que ha cursado
        cuatrimestres_cursados = list(range(1, cuatrimestre_actual))
        
        for cuatri in cuatrimestres_cursados:
            if cuatri in materias_por_cuatrimestre:
                materias_cuatri = materias_por_cuatrimestre[cuatri]
                
                for materia in materias_cuatri:
                    id_materia = materia[0]
                    
                    # Estudiantes regulares aprueban todo, irregulares pueden reprobar
                    if status == "Regular":
                        aprobada = True
                        calificacion = round(random.uniform(7.0, 10.0), 1)
                    else:
                        aprobada = random.random() < 0.8  # 80% de probabilidad de aprobar
                        calificacion = round(random.uniform(7.0, 10.0), 1) if aprobada else round(random.uniform(5.0, 6.9), 1)
                    
                    historial.append((id_estudiante, id_materia, calificacion, cuatri, aprobada))
    
    with open(os.path.join(carpeta, "historial_academico.csv"), 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["id_estudiante", "id_materia", "calificacion", "cuatrimestre", "aprobada"])
        writer.writerows(historial)
    
    return historial

def generar_preferencias(carpeta, estudiantes):
    """Genera preferencias_estudiante.csv."""
    preferencias = []
    
    for id_estudiante, nombre, cuatrimestre, status, creditos_acumulados, max_creditos in estudiantes:
        # Preferencia de horario
        preferencia_hora = random.choice(["mañana", "tarde", "noche"])
        
        # Días preferidos
        num_dias = random.randint(2, 5)
        dias_posibles = [1, 2, 3, 4, 5]  # Lunes a Viernes
        dias_preferidos = random.sample(dias_posibles, num_dias)
        dias_preferidos.sort()
        dias_str = ",".join(map(str, dias_preferidos))
        
        # Profesores preferidos
        profesores_preferidos = ""  # Dejar vacío por simplicidad
        
        preferencias.append((id_estudiante, preferencia_hora, dias_str, profesores_preferidos))
    
    with open(os.path.join(carpeta, "preferencias_estudiante.csv"), 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["id_estudiante", "preferencia_hora", "dias_preferidos", "profesores_preferidos"])
        writer.writerows(preferencias)
    
    return preferencias

def generar_todos_los_datos(carpeta="data"):
    """Genera todos los archivos CSV."""
    carpeta = crear_carpeta_datos(carpeta)
    print(f"Generando datos en carpeta: {carpeta}")
    
    print("Generando materias.csv...")
    materias = generar_materias(carpeta)
    
    print("Generando seriacion.csv...")
    seriacion = generar_seriacion(carpeta)
    
    print("Generando dependencias_proyectos.csv...")
    dependencias = generar_dependencias_proyectos(carpeta)
    
    print("Generando grupos.csv y horarios.csv...")
    grupos, horarios = generar_grupos_y_horarios(carpeta, materias)
    
    print("Generando estudiantes.csv...")
    estudiantes = generar_estudiantes(carpeta)
    
    print("Generando historial_academico.csv...")
    historial = generar_historial_academico(carpeta, estudiantes, materias)
    
    print("Generando preferencias_estudiante.csv...")
    preferencias = generar_preferencias(carpeta, estudiantes)
    
    print("Generando inscripciones.csv...")
    inscripciones = generar_inscripciones(carpeta, estudiantes, grupos, materias, seriacion)
    
    print("¡Datos generados con éxito!")
    print(f"Materias: {len(materias)}")
    print(f"Seriaciones: {len(seriacion)}")
    print(f"Dependencias: {len(dependencias)}")
    print(f"Grupos: {len(grupos)}")
    print(f"Horarios: {len(horarios)}")
    print(f"Estudiantes: {len(estudiantes)}")
    print(f"Registros de historial: {len(historial)}")
    print(f"Preferencias: {len(preferencias)}")
    print(f"Inscripciones: {len(inscripciones)}")

def generar_inscripciones(carpeta, estudiantes, grupos, materias, seriacion):
    """Genera inscripciones.csv."""
    from datetime import datetime
    
    inscripciones = []
    id_inscripcion = 1
    
    # Agrupar grupos por materia
    grupos_por_materia = {}
    # Corregimos esta parte: grupos es una lista de tuplas de 5 elementos
    for grupo_tupla in grupos:
        id_grupo, id_materia = grupo_tupla[0], grupo_tupla[1]  # Los dos primeros elementos
        if id_materia not in grupos_por_materia:
            grupos_por_materia[id_materia] = []
        grupos_por_materia[id_materia].append(id_grupo)
    
    # Fecha actual para inscripciones
    fecha_inscripcion = datetime.now().strftime("%Y-%m-%d")
    
    # Obtener IDs de materias de estadía
    materias_estadia = [m[0] for m in materias if m[5] == "Estadía"]
    
    for id_estudiante, nombre, cuatrimestre, status, creditos_acumulados, max_creditos in estudiantes:
        # Solo consideramos estudiantes en cuatrimestres activos (1-10)
        if not 1 <= cuatrimestre <= 10:
            continue
            
        # Determinar materias disponibles (considerando seriación)
        materias_disponibles = []
        for id_materia, nombre_materia, cuatri_materia, creditos, horas, tipo in materias:
            # Verificar que la materia corresponde al cuatrimestre actual o anterior
            if (status == "Regular" and cuatri_materia != cuatrimestre) or \
               (status == "Irregular" and cuatri_materia > cuatrimestre):
                continue
                
            # Verificar seriación (simplificada)
            prerequisitos_cumplidos = True
            for id_req, id_prereq in seriacion:
                if id_req == id_materia:
                    # Simplificación: Asumimos que los prerrequisitos están cumplidos
                    # En un caso real, habría que verificar el historial académico
                    pass
            
            if prerequisitos_cumplidos:
                materias_disponibles.append(id_materia)
        
        # Verificar si hay materias de estadía disponibles
        estadias_disponibles = [id_materia for id_materia in materias_disponibles 
                              if id_materia in materias_estadia]
        
        # Si hay estadías disponibles, solo se puede cursar esa materia
        if estadias_disponibles:
            id_estadia = estadias_disponibles[0]  # Tomar la primera estadía disponible
            
            if id_estadia in grupos_por_materia and grupos_por_materia[id_estadia]:
                id_grupo = random.choice(grupos_por_materia[id_estadia])
                
                inscripciones.append((
                    id_inscripcion,
                    id_estudiante,
                    id_grupo,
                    cuatrimestre,
                    fecha_inscripcion,
                    True  # activa
                ))
                
                id_inscripcion += 1
                
            # Si hay una estadía disponible, no se deben inscribir otras materias
            continue
        
        # Determinar número de materias a inscribir según tipo de estudiante
        if status == "Regular":
            num_materias = min(len(materias_disponibles), 7)  # Exactamente 7 materias para regulares
        else:
            num_materias = min(len(materias_disponibles), random.randint(3, 5))  # 3-5 materias para irregulares
        
        # Seleccionar materias priorizando las del cuatrimestre actual
        materias_cuatrimestre_actual = []
        materias_otros_cuatrimestres = []
        
        for id_materia in materias_disponibles:
            materia_data = next((m for m in materias if m[0] == id_materia), None)
            if materia_data and materia_data[2] == cuatrimestre:
                materias_cuatrimestre_actual.append(id_materia)
            else:
                materias_otros_cuatrimestres.append(id_materia)
        
        # Priorizar materias del cuatrimestre actual
        random.shuffle(materias_cuatrimestre_actual)
        random.shuffle(materias_otros_cuatrimestres)
        
        materias_seleccionadas = (materias_cuatrimestre_actual + 
                                 materias_otros_cuatrimestres)[:num_materias]
        
        # Inscribir en un grupo para cada materia
        for id_materia in materias_seleccionadas:
            if id_materia in grupos_por_materia and grupos_por_materia[id_materia]:
                id_grupo = random.choice(grupos_por_materia[id_materia])
                
                inscripciones.append((
                    id_inscripcion,
                    id_estudiante,
                    id_grupo,
                    cuatrimestre,
                    fecha_inscripcion,
                    True  # activa
                ))
                
                id_inscripcion += 1
    
    # Guardar a CSV
    with open(os.path.join(carpeta, "inscripciones.csv"), 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            "id_inscripcion", "id_estudiante", "id_grupo", 
            "cuatrimestre", "fecha_inscripcion", "activa"
        ])
        writer.writerows(inscripciones)
    
    return inscripciones

if __name__ == "__main__":
    generar_todos_los_datos()