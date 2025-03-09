from flask import Blueprint, jsonify, request
from services.data_loader import DataLoader
from services.optimizador import Optimizador
import traceback
import time

def register_api(app):
    """Registra el blueprint de la API en la aplicación Flask."""
    app.register_blueprint(api_bp, url_prefix='/api')
    
# Crear blueprint para la API
api_bp = Blueprint('api', __name__)

# Instancia global del DataLoader
data_loader = DataLoader()
data_loader.cargar_todo()

@api_bp.route('/estudiantes', methods=['GET'])
def obtener_estudiantes():
    """Devuelve la lista de todos los estudiantes."""
    try:
        estudiantes = []
        for id_estudiante, estudiante in data_loader.estudiantes.items():
            estudiantes.append({
                'id': id_estudiante,
                'nombre': estudiante.nombre,
                'cuatrimestre': estudiante.cuatrimestre,
                'status': estudiante.status,
                'creditos_acumulados': estudiante.creditos_acumulados,
                'materias_aprobadas': len(estudiante.materias_aprobadas)
            })
        
        return jsonify({
            'status': 'success',
            'data': estudiantes
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500

@api_bp.route('/materias', methods=['GET'])
def obtener_materias():
    """Devuelve la lista de todas las materias."""
    try:
        materias = []
        for id_materia, materia in data_loader.materias.items():
            materias.append(materia.to_dict())
        
        return jsonify({
            'status': 'success',
            'data': materias
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500

@api_bp.route('/estudiantes/<int:id_estudiante>', methods=['GET'])
def obtener_estudiante(id_estudiante):
    """Devuelve la información de un estudiante específico."""
    try:
        estudiante = data_loader.obtener_estudiante(id_estudiante)
        if not estudiante:
            return jsonify({
                'status': 'error',
                'message': 'Estudiante no encontrado'
            }), 404
        
        # Obtener materias aprobadas con sus nombres
        materias_aprobadas = []
        for id_materia in estudiante.materias_aprobadas:
            materia = data_loader.materias.get(id_materia)
            if materia:
                materias_aprobadas.append({
                    'id': id_materia,
                    'nombre': materia.nombre,
                    'cuatrimestre': materia.cuatrimestre,
                    'creditos': materia.creditos
                })
        
        # Obtener materias disponibles con sus nombres
        materias_disponibles = data_loader.obtener_materias_disponibles(estudiante)
        materias_disponibles_info = []
        for id_materia in materias_disponibles:
            materia = data_loader.materias.get(id_materia)
            if materia:
                materias_disponibles_info.append({
                    'id': id_materia,
                    'nombre': materia.nombre,
                    'cuatrimestre': materia.cuatrimestre,
                    'creditos': materia.creditos,
                    'tipo': materia.tipo
                })
        
        # Organizar materias disponibles por cuatrimestre
        materias_por_cuatrimestre = {}
        for materia in materias_disponibles_info:
            cuatrimestre = materia['cuatrimestre']
            if cuatrimestre not in materias_por_cuatrimestre:
                materias_por_cuatrimestre[cuatrimestre] = []
            materias_por_cuatrimestre[cuatrimestre].append(materia)
        
        return jsonify({
            'status': 'success',
            'data': {
                'id': estudiante.id,
                'nombre': estudiante.nombre,
                'cuatrimestre': estudiante.cuatrimestre,
                'status': estudiante.status,
                'creditos_acumulados': estudiante.creditos_acumulados,
                'max_creditos': estudiante.max_creditos,
                'materias_aprobadas': materias_aprobadas,
                'materias_disponibles': materias_disponibles_info,
                'materias_por_cuatrimestre': materias_por_cuatrimestre,
                'preferencias': estudiante.preferencias
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500

@api_bp.route('/estudiantes/<int:id_estudiante>/historial', methods=['GET'])
def obtener_historial(id_estudiante):
    """Devuelve el historial académico de un estudiante."""
    try:
        estudiante = data_loader.obtener_estudiante(id_estudiante)
        if not estudiante:
            return jsonify({
                'status': 'error',
                'message': 'Estudiante no encontrado'
            }), 404
        
        historial = data_loader.historial_academico.get(id_estudiante, [])
        historial_detallado = []
        
        for registro in historial:
            id_materia = registro['id_materia']
            materia = data_loader.materias.get(id_materia)
            if materia:
                historial_detallado.append({
                    'id_materia': id_materia,
                    'nombre_materia': materia.nombre,
                    'cuatrimestre_cursado': registro['cuatrimestre'],
                    'calificacion': registro['calificacion'],
                    'aprobada': registro['aprobada'],
                    'creditos': materia.creditos,
                    'tipo': materia.tipo
                })
        
        # Ordenar por cuatrimestre cursado y luego por nombre
        historial_detallado.sort(key=lambda x: (x['cuatrimestre_cursado'], x['nombre_materia']))
        
        return jsonify({
            'status': 'success',
            'data': historial_detallado
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500

@api_bp.route('/optimizar/<int:id_estudiante>', methods=['POST'])
def optimizar_horario(id_estudiante):
    """Optimiza el horario para un estudiante específico y genera un plan completo."""
    try:
        inicio = time.time()
        
        # Verificar que el estudiante existe
        estudiante = data_loader.obtener_estudiante(id_estudiante)
        if not estudiante:
            return jsonify({
                'status': 'error',
                'message': 'Estudiante no encontrado'
            }), 404
        
        # Obtener parámetros de la solicitud
        params = request.json or {}
        
        # Determinar si se solicita un plan completo o solo el cuatrimestre actual
        plan_completo = params.get('plan_completo', True)  # Por defecto generamos plan completo
        
        # Actualizar preferencias del estudiante si se proporcionan
        if 'preferencias' in params:
            nuevas_preferencias = params['preferencias']
            if 'preferencia_hora' in nuevas_preferencias:
                estudiante.preferencias['preferencia_hora'] = nuevas_preferencias['preferencia_hora']
            if 'dias_preferidos' in nuevas_preferencias:
                estudiante.preferencias['dias_preferidos'] = nuevas_preferencias['dias_preferidos']
        
        # Crear optimizador
        optimizador = Optimizador(
            materias=data_loader.materias,
            grupos=data_loader.grupos,
            seriacion=data_loader.seriacion,
            dependencias_proyectos=data_loader.dependencias_proyectos
        )
        
        # Inicializar la variable resultado
        resultado = None
        
        try:
            if plan_completo:
                # Generar plan completo hasta la graduación
                resultado = optimizador.planificar_trayectoria_completa(estudiante)
                
                # Añadir información del estudiante
                resultado['estudiante'] = {
                    'id': estudiante.id,
                    'nombre': estudiante.nombre,
                    'cuatrimestre': estudiante.cuatrimestre,
                    'status': estudiante.status,
                    'creditos_acumulados': estudiante.creditos_acumulados,
                    'max_creditos': estudiante.max_creditos
                }
                
            else:
                # Parámetros del algoritmo genético para un solo cuatrimestre
                tamano_poblacion = params.get('tamano_poblacion', 100)
                num_generaciones = params.get('num_generaciones', 30)
                tasa_cruce = params.get('tasa_cruce', 0.8)
                tasa_mutacion = params.get('tasa_mutacion', 0.2)
                
                # Obtener materias disponibles
                materias_disponibles = optimizador.get_materias_disponibles(estudiante)
                
                if not materias_disponibles:
                    return jsonify({
                        'status': 'warning',
                        'message': 'No hay materias disponibles para el estudiante con las restricciones actuales',
                        'data': {
                            'estudiante': {
                                'id': estudiante.id,
                                'nombre': estudiante.nombre,
                                'cuatrimestre': estudiante.cuatrimestre,
                                'status': estudiante.status
                            },
                            'materias_disponibles': []
                        }
                    })
                
                # Ejecutar algoritmo genético para el cuatrimestre actual
                mejor_horario = optimizador.optimizar_carga_academica(
                    estudiante,
                    tamano_poblacion=tamano_poblacion,
                    num_generaciones=num_generaciones,
                    tasa_cruce=tasa_cruce,
                    tasa_mutacion=tasa_mutacion
                )
                
                if not mejor_horario:
                    return jsonify({
                        'status': 'warning',
                        'message': 'No se pudo generar un horario válido con las restricciones dadas',
                        'data': {
                            'estudiante': {
                                'id': estudiante.id,
                                'nombre': estudiante.nombre,
                                'cuatrimestre': estudiante.cuatrimestre,
                                'status': estudiante.status
                            },
                            'materias_disponibles': materias_disponibles
                        }
                    })
                
                # Generar visualización del horario
                horario_semanal = optimizador.generar_horario_semanal(mejor_horario)
                
                # Obtener información detallada del horario
                materias_inscritas = []
                creditos_totales = 0
                
                for id_grupo in mejor_horario:
                    grupo = data_loader.grupos.get(id_grupo)
                    if grupo:
                        materia = data_loader.materias.get(grupo.id_materia)
                        if materia:
                            materias_inscritas.append({
                                'id_materia': materia.id,
                                'nombre_materia': materia.nombre,
                                'id_grupo': grupo.id,
                                'profesor': grupo.profesor,
                                'creditos': materia.creditos,
                                'cuatrimestre': materia.cuatrimestre,
                                'tipo': materia.tipo,
                                'horarios': grupo.horarios
                            })
                            creditos_totales += materia.creditos
                
                # Calcular distribución por día
                carga_por_dia = {}
                for dia in range(1, 6):  # Lunes a Viernes
                    carga_por_dia[dia] = 0
                
                for id_grupo in mejor_horario:
                    grupo = data_loader.grupos.get(id_grupo)
                    if grupo and grupo.horarios:
                        for dia, _, _, _ in grupo.horarios:
                            if 1 <= dia <= 5:  # Solo días hábiles
                                carga_por_dia[dia] += 1
                
                # Preparar resultado para un solo cuatrimestre
                resultado = {
                    'estudiante': {
                        'id': estudiante.id,
                        'nombre': estudiante.nombre,
                        'cuatrimestre': estudiante.cuatrimestre,
                        'status': estudiante.status
                    },
                    'creditos_totales': creditos_totales,
                    'num_materias': len(materias_inscritas),
                    'materias_inscritas': materias_inscritas,
                    'carga_por_dia': carga_por_dia,
                    'horario_semanal': horario_semanal,
                    'parametros': {
                        'tamano_poblacion': tamano_poblacion,
                        'num_generaciones': num_generaciones,
                        'tasa_cruce': tasa_cruce,
                        'tasa_mutacion': tasa_mutacion
                    }
                }
        except Exception as e:
            # Capturar errores específicos del optimizador
            import traceback
            error_trace = traceback.format_exc()
            print(f"Error en la optimización: {e}")
            print(error_trace)
            
            return jsonify({
                'status': 'error',
                'message': f'Error durante la optimización: {str(e)}',
                'traceback': error_trace
            }), 500
        
        # Verificar que se haya generado un resultado
        if resultado is None:
            return jsonify({
                'status': 'error',
                'message': 'No se pudo generar ningún resultado de optimización'
            }), 500
        
        # Calcular tiempo de ejecución
        fin = time.time()
        tiempo_ejecucion = round(fin - inicio, 2)
        
        # Añadir tiempo de ejecución al resultado
        resultado['tiempo_ejecucion'] = tiempo_ejecucion
        
        return jsonify({
            'status': 'success',
            'message': f'Horario optimizado generado en {tiempo_ejecucion} segundos',
            'data': resultado
        })
        
    except Exception as e:
        # Capturar errores generales
        return jsonify({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500
    
@api_bp.route('/estudiantes/<int:id_estudiante>/horario', methods=['GET'])
def obtener_horario_estudiante(id_estudiante):
    """Devuelve el horario actual de un estudiante."""
    try:
        # Verificar que el estudiante existe
        estudiante = data_loader.obtener_estudiante(id_estudiante)
        if not estudiante:
            return jsonify({
                'status': 'error',
                'message': 'Estudiante no encontrado'
            }), 404
        
        # Obtener los grupos en los que está inscrito
        grupos_inscritos = data_loader.obtener_grupos_inscritos(id_estudiante)
        
        if not grupos_inscritos:
            return jsonify({
                'status': 'warning',
                'message': 'El estudiante no tiene materias inscritas actualmente',
                'data': {
                    'estudiante': {
                        'id': estudiante.id,
                        'nombre': estudiante.nombre,
                        'cuatrimestre': estudiante.cuatrimestre,
                        'status': estudiante.status
                    },
                    'materias_inscritas': [],
                    'creditos_totales': 0,
                    'num_materias': 0,
                    'carga_por_dia': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
                    'horario_semanal': {}
                }
            })
        
        # Obtener información detallada de cada materia inscrita
        materias_inscritas = []
        creditos_totales = 0
        
        for id_grupo in grupos_inscritos:
            grupo = data_loader.grupos.get(id_grupo)
            if grupo:
                materia = data_loader.materias.get(grupo.id_materia)
                if materia:
                    materias_inscritas.append({
                        'id_materia': materia.id,
                        'nombre_materia': materia.nombre,
                        'id_grupo': grupo.id,
                        'profesor': grupo.profesor,
                        'creditos': materia.creditos,
                        'cuatrimestre': materia.cuatrimestre,
                        'tipo': materia.tipo,
                        'horarios': grupo.horarios
                    })
                    creditos_totales += materia.creditos
        
        # Calcular distribución por día
        carga_por_dia = {}
        for dia in range(1, 6):  # Lunes a Viernes
            carga_por_dia[dia] = 0
        
        for id_grupo in grupos_inscritos:
            grupo = data_loader.grupos.get(id_grupo)
            if grupo and hasattr(grupo, 'horarios') and grupo.horarios:
                for dia, _, _, _ in grupo.horarios:
                    if 1 <= dia <= 5:  # Solo días hábiles
                        carga_por_dia[dia] += 1
        
        # Generar visualización del horario
        optimizador = Optimizador(
            materias=data_loader.materias,
            grupos=data_loader.grupos,
            seriacion=data_loader.seriacion,
            dependencias_proyectos=data_loader.dependencias_proyectos
        )
        horario_semanal = optimizador.generar_horario_semanal(grupos_inscritos)
        
        return jsonify({
            'status': 'success',
            'data': {
                'estudiante': {
                    'id': estudiante.id,
                    'nombre': estudiante.nombre,
                    'cuatrimestre': estudiante.cuatrimestre,
                    'status': estudiante.status
                },
                'creditos_totales': creditos_totales,
                'num_materias': len(materias_inscritas),
                'materias_inscritas': materias_inscritas,
                'carga_por_dia': carga_por_dia,
                'horario_semanal': horario_semanal
            }
        })
    except Exception as e:
        import traceback
        print(f"Error en obtener_horario_estudiante: {e}")
        print(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500