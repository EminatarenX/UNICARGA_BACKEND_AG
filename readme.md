Estructura del Algoritmo Genético para UNICARGA

El sistema UNICARGA implementa un algoritmo genético para optimizar la carga académica de los estudiantes. A continuación, se describe la estructura general del modelo sin entrar en detalles de código.
Estructura del Individuo

En este algoritmo, cada individuo representa una solución potencial al problema de carga académica:
Individuo (Horario)

Un horario es una lista de IDs de grupos en los que el estudiante estaría inscrito. Ejemplo:
[id_grupo_1, id_grupo_5, id_grupo_12, id_grupo_24, id_grupo_30]

Cada individuo es único y representa una combinación específica de grupos que conforman un horario completo.
Clases Principales

El sistema está compuesto por varias clases que gestionan diferentes aspectos:
Materia

    Atributos: ID, nombre, cuatrimestre, créditos, horas totales, tipo.

Grupo

Representa un grupo específico de una materia.

    Atributos: ID, ID de materia, profesor, cupo máximo, cupo actual, horarios.

Estudiante

Contiene la información de cada estudiante.

    Atributos: ID, nombre, cuatrimestre actual, status (Regular/Irregular), créditos acumulados, materias aprobadas, preferencias.

Horario

Gestiona la representación de un horario semanal.

    Métodos: Agregar grupos, verificar conflictos, calcular estadísticas.

Optimizador

Implementa el algoritmo genético para encontrar horarios óptimos.

    Responsabilidad: Gestiona la evolución, operadores genéticos y evaluación de fitness.

Componentes del Algoritmo Genético
1. Generación de Población Inicial

La población inicial se genera considerando:

    Materias disponibles según seriación (prerrequisitos).
    Grupos disponibles para esas materias.
    Restricciones de cupo.
    Preferencias del estudiante.

El algoritmo crea varios horarios aleatorios pero viables, verificando:

    Conflictos de horario entre grupos.
    Cupo disponible en los grupos.
    Regulaciones académicas (ejemplo: los estudiantes regulares deben tener exactamente 7 materias).

2. Función de Fitness

La evaluación de cada individuo se realiza mediante una función de fitness que considera:
Número de materias:

    Regulares: Penalización si no tiene exactamente 7 materias.
    Irregulares: Se premia tener un número óptimo de materias (hasta 5).

Distribución de carga:

    Analiza clases por día y penaliza horarios desbalanceados.
    Usa la desviación estándar para medir el balance entre días.

Priorización de materias:

    Irregulares: Mayor valor a materias de cuatrimestres anteriores.
    Ambos: Priorización de materias que son prerrequisito de otras.

Preferencias del estudiante:

    Horario preferido (mañana, tarde, noche).
    Días preferidos de la semana.
    Profesores preferidos.

Casos especiales:

    Reglas para estadías (deben ser la única materia inscrita).
    No exceder el máximo de créditos permitidos.

3. Selección de Padres

Se realiza mediante el método de selección por torneo:

    Se seleccionan aleatoriamente 2-3 individuos de la población.
    Se elige al de mayor fitness entre ellos.
    Este proceso se repite para seleccionar múltiples padres.

4. Operadores Genéticos
Cruce

Se implementa un cruce de un punto entre dos padres:

    Se selecciona un punto aleatorio y se intercambian secciones de ambos padres.

Ejemplo:

Padre 1: [G1, G3, G5, G7, G9]
Padre 2: [G2, G4, G6, G8, G10]
Punto de cruce: 2
Hijo 1: [G1, G3, G6, G8, G10]
Hijo 2: [G2, G4, G5, G7, G9]

Mutación

La mutación puede ocurrir de dos formas:

    Cambio de grupo: Se reemplaza un grupo por otro que imparta la misma materia.
    Cambio de materia: Se sustituye una materia por otra disponible, verificando que no haya conflictos.

La tasa de mutación controla la frecuencia de estos cambios.
5. Elitismo

El mejor individuo de cada generación se conserva en la siguiente. Esto garantiza que la solución óptima nunca se pierda durante la evolución.
6. Casos Especiales

El sistema maneja situaciones particulares:

    Estadías: Cuando una estadía está disponible, se prioriza como única materia a cursar.
    Estudiantes regulares: Deben cursar exactamente 7 materias o todas las de su cuatrimestre.
    Estudiantes irregulares: Mayor flexibilidad, priorizando materias atrasadas.
    Seriación: Verificación de prerrequisitos.
    Proyectos integradores: Verificación de dependencias específicas.

7. Planificación de Trayectoria Completa

El sistema puede generar un plan completo hasta la graduación:

    Simula cuatrimestre por cuatrimestre, actualizando las materias aprobadas.
    Genera un horario óptimo para cada cuatrimestre futuro.
    Calcula estadísticas como cuatrimestres restantes y fecha estimada de graduación.

Generación de Datos y Validaciones Lógicas en UNICARGA
1. Generación de Datos
Generación del Plan de Estudios

    Materias: Se genera un plan de estudios completo de 10 cuatrimestres con 58 materias.
        Materias regulares: Cuatrimestres 1-5, 7-9.
        Estadías: Cuatrimestres 6 y 10.
        Proyectos integradores: Cuatrimestres 3, 5 y 9.
    Horas y Créditos:
        Las horas varían de 60 a 105 para materias regulares.
        Las estadías tienen 600 horas.
        Los créditos se calculan proporcionalmente a las horas totales.

Configuración de Seriación y Dependencias

    Seriación: Define qué materias son prerrequisito de otras.
    Dependencias de Proyectos: Define las materias que deben aprobarse antes de los proyectos integradores.

Generación de Grupos y Horarios

    Grupos: Se crean 2-3 grupos por materia con horarios y cupos.
    Horarios: Las sesiones se distribuyen mayormente en horarios diurnos.

Generación de Estudiantes

    Datos Demográficos: Se crean perfiles de estudiantes con nombres, asignación de cuatrimestres y estados académicos.
    Historial Académico: Se simulan materias aprobadas, calificaciones y patrones de aprobación.
    Preferencias: Se asignan preferencias aleatorias para horarios y días.

Generación de Inscripciones Actuales

    Se simulan inscripciones considerando la seriación y compatibilidad horaria.

2. Validaciones Lógicas para la Optimización
Validaciones de Requisitos Académicos

    Verificación de Prerrequisitos: Se verifica que el estudiante haya aprobado todos los prerrequisitos.
    Validación de Tipo de Estudiante: Para estudiantes regulares e irregulares.

Validaciones de Horario

    Detección de Conflictos Horarios: Verifica que no haya superposición de clases.
    Balanceo de Carga: Penaliza horarios desbalanceados.

Validaciones de Créditos

    Límite de Créditos: No debe exceder el máximo permitido.
    Eficiencia de Créditos: Se premian los horarios que aprovechan mejor los créditos.

Validaciones de Preferencias

    Compatibilidad con Preferencias: Se evalúa qué tan bien el horario se ajusta a las preferencias del estudiante.

Validaciones para la Planificación Completa

    Progresión Académica: Se verifica el avance lógico del estudiante.
    Estimación Realista de Graduación: Se calcula la fecha estimada de graduación.