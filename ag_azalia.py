import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import base64
from io import BytesIO
from PIL import Image, ImageTk
import json
from datetime import datetime, timedelta
import os
import sys
import random

# Importar la clase AlgoritmoGeneticoGasolina
class AlgoritmoGeneticoGasolina:
    def __init__(self, ruta_csv='datos_gasolineras_tuxtla.csv'):
        # Cargar datos de gasolineras
        self.df = pd.read_csv(ruta_csv)
        self.gasolineras = self.df['gasolinera_id'].unique()
        self.nombres_gasolineras = dict(zip(self.df['gasolinera_id'], self.df['nombre']))
        self.ubicaciones = dict(zip(self.df['gasolinera_id'], self.df['ubicacion']))
        self.capacidades = dict(zip(self.df['gasolinera_id'], self.df['capacidad_total']))
        self.inventarios = dict(zip(self.df['gasolinera_id'], self.df['inventario_actual']))
        
        # Parámetros del algoritmo genético
        self.tamano_poblacion = 50
        self.tasa_mutacion = 0.1
        self.num_generaciones = 100
        self.elitismo = 5
        
        # Restricciones
        self.capacidad_camion = 20000  # litros
        self.costo_por_km = 15  # pesos por kilómetro
        self.velocidad_promedio = 40  # km/h
        self.tiempo_descarga = 30  # minutos por descarga
        
        # Matriz de distancias (simulada para este ejemplo)
        self.distancias = self._generar_matriz_distancias()
        
    def _generar_matriz_distancias(self):
        """Genera una matriz de distancias entre gasolineras basada en coordenadas"""
        n = len(self.gasolineras)
        matriz = np.zeros((n+1, n+1))  # +1 para incluir el depósito central (id 0)
        
        # Extraer coordenadas de cada ubicación
        coordenadas = {}
        coordenadas[0] = (16.75, -93.15)  # Depósito central (simulado)
        
        for gid, ubicacion in self.ubicaciones.items():
            try:
                lat, lon = map(float, ubicacion.split(','))
                coordenadas[gid] = (lat, lon)
            except:
                coordenadas[gid] = (16.7, -93.1)  # Valor por defecto si hay error
        
        # Calcular distancias euclidianas (simplificado)
        for i in range(n+1):
            id_i = 0 if i == 0 else self.gasolineras[i-1]
            for j in range(n+1):
                id_j = 0 if j == 0 else self.gasolineras[j-1]
                
                if i == j:
                    matriz[i, j] = 0
                else:
                    # Distancia euclidiana (podría reemplazarse por distancia real)
                    lat1, lon1 = coordenadas[id_i]
                    lat2, lon2 = coordenadas[id_j]
                    dist = np.sqrt((lat1-lat2)*2 + (lon1-lon2)*2) * 111  # Aproximación a km
                    matriz[i, j] = dist
        
        return matriz
    
    def _predecir_demanda(self, gasolinera_id, dias=7):
        """Predice la demanda para una gasolinera en los próximos días"""
        datos_gasolinera = self.df[self.df['gasolinera_id'] == gasolinera_id]
        
        # Promedio entre los valores min y max para la simulación
        clientes_prom = (datos_gasolinera['clientes_min'].values[0] + datos_gasolinera['clientes_max'].values[0]) / 2
        vehiculos_prom = (datos_gasolinera['vehiculos_min'].values[0] + datos_gasolinera['vehiculos_max'].values[0]) / 2
        litros_prom = (datos_gasolinera['litros_promedio_min'].values[0] + datos_gasolinera['litros_promedio_max'].values[0]) / 2
        desv_std = (datos_gasolinera['desviacion_estandar_min'].values[0] + datos_gasolinera['desviacion_estandar_max'].values[0]) / 2
        
        # Simulación de demanda diaria
        demanda_diaria = []
        for _ in range(dias):
            # Número de clientes en el día (con algo de variabilidad)
            clientes_dia = int(np.random.normal(clientes_prom * 12, clientes_prom * 3))
            
            # Porcentaje de clientes que compran gasolina
            porcentaje_compra = random.uniform(0.6, 0.9)
            
            # Simulación del consumo
            demanda = 0
            for _ in range(int(clientes_dia * porcentaje_compra)):
                litros = max(5, np.random.normal(litros_prom, desv_std))
                demanda += litros
            
            demanda_diaria.append(int(demanda))
        
        return demanda_diaria
    
    def _generar_individuo(self, gasolineras, dias=7):
        """Genera un plan de distribución (individuo) aleatorio basado en las gasolineras seleccionadas"""
        individuo = []
        
        for dia in range(dias):
            num_rutas = random.randint(1, min(5, len(gasolineras)))
            rutas_dia = []
            gasolineras_disponibles = gasolineras.copy()  # Evita modificar la lista original
            
            for _ in range(num_rutas):
                if not gasolineras_disponibles:
                    break
                    
                num_paradas = random.randint(1, min(4, len(gasolineras_disponibles)))
                gasolineras_ruta = random.sample(gasolineras_disponibles, num_paradas)
                
                for g in gasolineras_ruta:
                    gasolineras_disponibles.remove(g)
                
                litros_restantes = self.capacidad_camion
                litros_por_gasolinera = {}
                
                for g in gasolineras_ruta:
                    capacidad_disponible = self.capacidades[g] - self.inventarios[g]
                    demanda_predicha = sum(self._predecir_demanda(g, 3))
                    
                    litros = min(
                        random.randint(5000, 15000),
                        capacidad_disponible,
                        max(1000, demanda_predicha),
                        litros_restantes
                    )
                    
                    if litros > 1000:
                        litros_por_gasolinera[g] = int(litros)
                        litros_restantes -= litros
                
                secuencia = [g for g in gasolineras_ruta if g in litros_por_gasolinera]
                
                if secuencia:
                    hora_salida = random.randint(6, 16)
                    
                    rutas_dia.append({
                        "secuencia": secuencia,
                        "litros": litros_por_gasolinera,
                        "hora_salida": f"{hora_salida}:00"
                    })
            
            individuo.append(rutas_dia)
        
        return individuo


    def _calcular_fitness(self, individuo, gasolineras):
        """Evalúa la calidad de un plan de distribución basado en las gasolineras seleccionadas"""
        costo_total = 0
        beneficio_total = 0
        
        for rutas_dia in individuo:
            for ruta in rutas_dia:
                secuencia = [g for g in ruta["secuencia"] if g in gasolineras]  # Filtrar por gasolineras seleccionadas
                litros = {g: ruta["litros"][g] for g in secuencia if g in ruta["litros"]}
                
                if not secuencia:
                    continue
                
                distancia_total = 0
                punto_anterior = 0  # Depósito central
                
                for g in secuencia:
                    idx_g = np.where(self.gasolineras == g)[0][0] + 1
                    distancia_total += self.distancias[punto_anterior, idx_g]
                    punto_anterior = idx_g
                
                # Regreso al depósito central
                distancia_total += self.distancias[punto_anterior, 0]
                
                costo_transporte = distancia_total * self.costo_por_km
                tiempo_viaje = distancia_total / self.velocidad_promedio
                tiempo_descarga = len(secuencia) * (self.tiempo_descarga / 60)
                tiempo_total = tiempo_viaje + tiempo_descarga
                
                # Penalización por hora tardía
                hora_salida = int(ruta["hora_salida"].split(":")[0])
                hora_llegada = hora_salida + tiempo_total
                
                if hora_llegada > 20:  # Fuera de horario
                    costo_total += 5000  # Penalización
                
                # Costo operativo
                costo_ruta = costo_transporte + (tiempo_total * 200)  # Costo por tiempo
                costo_total += costo_ruta
                
                # Beneficio (simplificado)
                beneficio_ruta = sum(litros.values()) * 0.5  # Ganancia por litro
                beneficio_total += beneficio_ruta
        
        return beneficio_total - costo_total
    
    def _seleccionar_padres(self, poblacion, fitness):
        """Selecciona individuos para reproducción mediante torneo"""
        padres = []
        
        for _ in range(len(poblacion)):
            # Selección por torneo (tamaño 3)
            indices_torneo = random.sample(range(len(poblacion)), 3)
            
            # Elegir el mejor del torneo
            idx_ganador = indices_torneo[0]
            for idx in indices_torneo[1:]:
                if fitness[idx] > fitness[idx_ganador]:
                    idx_ganador = idx
            
            padres.append(poblacion[idx_ganador])
        
        return padres
    
    def _cruzar(self, padre1, padre2):
        """Operador de cruce para dos planes de distribución"""
        if not padre1 or not padre2:
            return padre1 if padre1 else padre2
            
        # Asegurarse de que ambos tengan la misma longitud (días)
        min_dias = min(len(padre1), len(padre2))
        
        hijo = []
        
        # Para cada día, seleccionar rutas de uno u otro padre
        for dia in range(min_dias):
            # Decidir si tomar rutas del padre1, padre2 o mezclar
            opcion = random.randint(0, 2)
            
            if opcion == 0:  # Tomar del padre1
                hijo.append(padre1[dia].copy())
            elif opcion == 1:  # Tomar del padre2
                hijo.append(padre2[dia].copy())
            else:  # Mezclar rutas
                rutas_mezcladas = []
                
                # Tomar algunas rutas de cada padre
                num_rutas_p1 = len(padre1[dia]) if dia < len(padre1) else 0
                num_rutas_p2 = len(padre2[dia]) if dia < len(padre2) else 0
                
                if num_rutas_p1 > 0:
                    rutas_p1 = random.sample(padre1[dia], max(1, num_rutas_p1 // 2))
                    rutas_mezcladas.extend(rutas_p1)
                
                if num_rutas_p2 > 0:
                    rutas_p2 = random.sample(padre2[dia], max(1, num_rutas_p2 // 2))
                    rutas_mezcladas.extend(rutas_p2)
                
                hijo.append(rutas_mezcladas)
        
        return hijo
    
    def _mutar(self, individuo):
        """Operador de mutación para un plan de distribución"""
        # Clonar el individuo para no modificar el original
        mutado = [dia.copy() for dia in individuo]
        
        # Diferentes tipos de mutación
        tipo_mutacion = random.randint(0, 3)
        
        if tipo_mutacion == 0:
            # Cambiar la hora de salida de una ruta aleatoria
            if mutado:  # Verificar que hay días
                dia = random.randint(0, len(mutado) - 1)
                
                if mutado[dia]:  # Verificar que hay rutas en ese día
                    ruta_idx = random.randint(0, len(mutado[dia]) - 1)
                    nueva_hora = random.randint(6, 16)
                    mutado[dia][ruta_idx]["hora_salida"] = f"{nueva_hora}:00"
        
        elif tipo_mutacion == 1:
            # Modificar la cantidad de litros en una gasolinera
            if mutado:  # Verificar que hay días
                dia = random.randint(0, len(mutado) - 1)
                
                if mutado[dia]:  # Verificar que hay rutas en ese día
                    ruta_idx = random.randint(0, len(mutado[dia]) - 1)
                    
                    if mutado[dia][ruta_idx]["secuencia"]:  # Verificar que hay gasolineras
                        g = random.choice(mutado[dia][ruta_idx]["secuencia"])
                        
                        # Aumentar o disminuir litros (+-20%)
                        cambio = random.uniform(0.8, 1.2)
                        litros_actuales = mutado[dia][ruta_idx]["litros"][g]
                        nuevos_litros = int(litros_actuales * cambio)
                        
                        # Asegurar que esté entre límites razonables
                        mutado[dia][ruta_idx]["litros"][g] = max(1000, min(15000, nuevos_litros))
                        
        elif tipo_mutacion == 2:
            # Cambiar el orden de visita en una ruta
            if mutado:  # Verificar que hay días
                dia = random.randint(0, len(mutado) - 1)
                
                if mutado[dia]:  # Verificar que hay rutas en ese día
                    ruta_idx = random.randint(0, len(mutado[dia]) - 1)
                    
                    # Si hay más de una gasolinera, cambiar el orden
                    if len(mutado[dia][ruta_idx]["secuencia"]) > 1:
                        random.shuffle(mutado[dia][ruta_idx]["secuencia"])
        
        elif tipo_mutacion == 3:
            # Agregar o quitar una gasolinera de una ruta
            if mutado:  # Verificar que hay días
                dia = random.randint(0, len(mutado) - 1)
                
                if mutado[dia]:  # Verificar que hay rutas en ese día
                    ruta_idx = random.randint(0, len(mutado[dia]) - 1)
                    
                    # 50% probabilidad de agregar, 50% de quitar
                    if random.random() < 0.5 and len(mutado[dia][ruta_idx]["secuencia"]) > 1:
                        # Quitar una gasolinera
                        g_quitar = random.choice(mutado[dia][ruta_idx]["secuencia"])
                        mutado[dia][ruta_idx]["secuencia"].remove(g_quitar)
                        if g_quitar in mutado[dia][ruta_idx]["litros"]:
                            del mutado[dia][ruta_idx]["litros"][g_quitar]
                    else:
                        # Agregar una gasolinera (si hay disponibles)
                        gasolineras_actuales = set(mutado[dia][ruta_idx]["secuencia"])
                        gasolineras_disponibles = set(self.gasolineras) - gasolineras_actuales
                        
                        if gasolineras_disponibles:
                            g_nueva = random.choice(list(gasolineras_disponibles))
                            mutado[dia][ruta_idx]["secuencia"].append(g_nueva)
                            
                            # Asignar litros
                            capacidad_disponible = self.capacidades[g_nueva] - self.inventarios[g_nueva]
                            litros = min(
                                random.randint(5000, 15000),
                                capacidad_disponible
                            )
                            mutado[dia][ruta_idx]["litros"][g_nueva] = litros
        
        return mutado
        
    def optimizar(self, dias=7, gasolineras=None):
        """Ejecuta el algoritmo genético para optimizar la distribución considerando gasolineras."""
        
        if gasolineras is None:
            gasolineras = self.gasolineras
            
        # Convertir a lista si es necesario
        if not isinstance(gasolineras, list):
            gasolineras = list(gasolineras)
            
        # Verificar parámetros
        if not isinstance(dias, int):
            raise ValueError("El parámetro 'dias' debe ser un número entero")
        
        if not isinstance(gasolineras, list):
            raise ValueError("El parámetro 'gasolineras' debe ser una lista")

        # Generar población inicial
        poblacion = [self._generar_individuo(gasolineras, dias) for _ in range(self.tamano_poblacion)]
        
        mejor_fitness_historico = []
        mejor_individuo = None
        mejor_fitness = float('-inf')

        for generacion in range(self.num_generaciones):
            fitness = [self._calcular_fitness(individuo, gasolineras) for individuo in poblacion]

            idx_mejor = fitness.index(max(fitness))
            if fitness[idx_mejor] > mejor_fitness:
                mejor_individuo = poblacion[idx_mejor]
                mejor_fitness = fitness[idx_mejor]

            mejor_fitness_historico.append(max(fitness))

            elite = [poblacion[i] for i in sorted(range(len(fitness)), key=lambda i: fitness[i], reverse=True)[:self.elitismo]]
            padres = self._seleccionar_padres(poblacion, fitness)

            nueva_poblacion = elite.copy()
            while len(nueva_poblacion) < self.tamano_poblacion:
                padre1, padre2 = random.sample(padres, 2)
                hijo = self._cruzar(padre1, padre2)

                if random.random() < self.tasa_mutacion:
                    hijo = self._mutar(hijo)

                nueva_poblacion.append(hijo)

            poblacion = nueva_poblacion

        print(f"Optimización completada. Mejor fitness: {mejor_fitness:.2f}")
        return mejor_individuo, mejor_fitness, mejor_fitness_historico

    def generar_reporte(self, mejor_plan, dias=7):
        """Genera un reporte detallado del plan optimizado"""
        # Inicializar reporte
        reporte = {
            "plan_distribucion": [],
            "metricas": {},
            "graficos": {}
        }
        
        # Calcular métricas para cada día
        costo_total = 0
        beneficio_total = 0
        km_total = 0
        litros_entregados = 0
        
        # Procesar cada día
        for dia, rutas_dia in enumerate(mejor_plan):
            dia_actual = (datetime.now() + timedelta(days=dia)).strftime('%Y-%m-%d')
            
            plan_dia = {
                "fecha": dia_actual,
                "rutas": []
            }
            
            # Procesar cada ruta
            for idx, ruta in enumerate(rutas_dia):
                secuencia = ruta["secuencia"]
                litros = ruta["litros"]
                hora_salida = ruta["hora_salida"]
                
                if not secuencia:
                    continue
                
                # Calcular métricas de la ruta
                distancia_total = 0
                punto_anterior = 0  # Depósito central
                
                paradas = []
                
                for g in secuencia:
                    # Índice en la matriz de distancias
                    idx_g = np.where(self.gasolineras == g)[0][0] + 1
                    
                    # Agregar distancia
                    distancia = self.distancias[punto_anterior, idx_g]
                    distancia_total += distancia
                    
                    # Tiempo de llegada
                    tiempo_acumulado = distancia_total / self.velocidad_promedio
                    hora_base = int(hora_salida.split(":")[0])
                    minutos_base = int(hora_salida.split(":")[1]) if ":" in hora_salida else 0
                    horas_extra = int(tiempo_acumulado)
                    minutos_extra = int((tiempo_acumulado - horas_extra) * 60)
                    
                    hora_llegada = (hora_base + horas_extra) % 24
                    minutos_llegada = (minutos_base + minutos_extra) % 60
                    
                    # Hora de llegada formateada
                    hora_llegada_str = f"{hora_llegada:02d}:{minutos_llegada:02d}"
                    
                    # Agregar parada
                    paradas.append({
                        "gasolinera_id": int(g),
                        "nombre": self.nombres_gasolineras[g],
                        "litros_entregados": litros[g],
                        "hora_llegada": hora_llegada_str,
                        "distancia_km": round(distancia, 2)
                    })
                    
                    punto_anterior = idx_g
                    litros_entregados += litros[g]
                
                # Regreso al depósito
                distancia_regreso = self.distancias[punto_anterior, 0]
                distancia_total += distancia_regreso
                
                # Costo de transporte
                costo_transporte = distancia_total * self.costo_por_km
                
                # Tiempo total de la ruta
                tiempo_viaje = distancia_total / self.velocidad_promedio  # horas
                tiempo_descarga = len(secuencia) * (self.tiempo_descarga / 60)  # horas
                tiempo_total = tiempo_viaje + tiempo_descarga
                
                # Beneficio de la ruta
                beneficio_ruta = sum(litros.values()) * 0.5  # 0.5 pesos por litro
                
                # Agregar ruta al plan
                plan_dia["rutas"].append({
                    "id_ruta": idx + 1,
                    "hora_salida": hora_salida,
                    "distancia_total": round(distancia_total, 2),
                    "tiempo_estimado": round(tiempo_total, 2),
                    "costo_transporte": round(costo_transporte, 2),
                    "beneficio": round(beneficio_ruta, 2),
                    "litros_totales": sum(litros.values()),
                    "paradas": paradas
                })
                
                # Actualizar métricas globales
                costo_total += costo_transporte
                beneficio_total += beneficio_ruta
                km_total += distancia_total
            
            reporte["plan_distribucion"].append(plan_dia)
        
        # Métricas globales
        reporte["metricas"] = {
            "costo_total": round(costo_total, 2),
            "beneficio_total": round(beneficio_total, 2),
            "beneficio_neto": round(beneficio_total - costo_total, 2),
            "kilometros_totales": round(km_total, 2),
            "litros_entregados": litros_entregados,
            "numero_rutas": sum(len(dia["rutas"]) for dia in reporte["plan_distribucion"]),
            "costo_por_litro": round(costo_total / litros_entregados if litros_entregados > 0 else 0, 2),
            "rendimiento": round(beneficio_total / costo_total if costo_total > 0 else 0, 2)
        }
        
        # Simular sistema actual para comparación
        costo_actual = costo_total * 1.3  # 30% más caro
        beneficio_actual = beneficio_total * 0.85  # 15% menos beneficio
        
        reporte["comparacion"] = {
            "costo_actual": round(costo_actual, 2),
            "beneficio_actual": round(beneficio_actual, 2),
            "beneficio_neto_actual": round(beneficio_actual - costo_actual, 2),
            "ahorro_costo": round(costo_actual - costo_total, 2),
            "incremento_beneficio": round(beneficio_total - beneficio_actual, 2),
            "mejora_porcentual": round(
                ((beneficio_total - costo_total) - (beneficio_actual - costo_actual)) /
                abs(beneficio_actual - costo_actual) * 100 if (beneficio_actual - costo_actual) != 0 else 0,
                2
            )
        }
        
        # Generar datos para gráficos
        self._generar_datos_graficos(reporte)
        
        return reporte
    
    def _generar_datos_graficos(self, reporte):
        """Genera datos para los gráficos del reporte"""
        # Gráfico de distribución de litros por día
        litros_por_dia = []
        
        for dia in reporte["plan_distribucion"]:
            fecha = dia["fecha"]
            litros_dia = sum(ruta["litros_totales"] for ruta in dia["rutas"]) if dia["rutas"] else 0
            litros_por_dia.append({"fecha": fecha, "litros": litros_dia})
        
        reporte["graficos"]["litros_por_dia"] = litros_por_dia
        
        # Gráfico de distribución por gasolinera
        litros_por_gasolinera = {}
        rutas_por_gasolinera = {}
        
        for dia in reporte["plan_distribucion"]:
            for ruta in dia["rutas"]:
                for parada in ruta["paradas"]:
                    gid = parada["gasolinera_id"]
                    nombre = parada["nombre"]
                    litros = parada["litros_entregados"]
                    
                    if gid not in litros_por_gasolinera:
                        litros_por_gasolinera[gid] = {"nombre": nombre, "litros": 0}
                        rutas_por_gasolinera[gid] = 0
                    
                    litros_por_gasolinera[gid]["litros"] += litros
                    rutas_por_gasolinera[gid] += 1
        
        reporte["graficos"]["distribucion_por_gasolinera"] = [
            {"id": gid, "nombre": info["nombre"], "litros": info["litros"]}
            for gid, info in litros_por_gasolinera.items()
        ]
        
        reporte["graficos"]["rutas_por_gasolinera"] = [
            {"id": gid, "nombre": litros_por_gasolinera[gid]["nombre"], "rutas": num_rutas}
            for gid, num_rutas in rutas_por_gasolinera.items()
        ]
        
        # Comparativa optimizado vs actual
        reporte["graficos"]["comparativa"] = [
            {"concepto": "Costo", "optimizado": reporte["metricas"]["costo_total"], "actual": reporte["comparacion"]["costo_actual"]},
            {"concepto": "Beneficio", "optimizado": reporte["metricas"]["beneficio_total"], "actual": reporte["comparacion"]["beneficio_actual"]},
            {"concepto": "Beneficio Neto", "optimizado": reporte["metricas"]["beneficio_neto"], "actual": reporte["comparacion"]["beneficio_neto_actual"]}
        ]
    
    def generar_prediccion_demanda(self, gasolineras_seleccionadas, dias=7):
        """Genera predicciones de demanda para las gasolineras seleccionadas"""
        predicciones = {}
        
        for gid in gasolineras_seleccionadas:
            # Verificar que la gasolinera existe en los datos
            if gid in self.gasolineras:
                demanda_diaria = self._predecir_demanda(gid, dias)
                fechas = [(datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(dias)]
                
                predicciones[gid] = {
                    "nombre": self.nombres_gasolineras[gid],
                    "datos": [{"fecha": fecha, "demanda": demanda} for fecha, demanda in zip(fechas, demanda_diaria)]
                }
        
        return predicciones
    
    def generar_graficos_resultados(self, reporte):
        """Genera gráficos para el reporte de optimización"""
        graficos = {}
        
        # Gráfico de distribución de litros por día
        if "litros_por_dia" in reporte["graficos"]:
            plt.figure(figsize=(10, 5))
            fechas = [item["fecha"] for item in reporte["graficos"]["litros_por_dia"]]
            litros = [item["litros"] for item in reporte["graficos"]["litros_por_dia"]]
            
            plt.bar(fechas, litros, color='#4CAF50')
            plt.title('Distribución de Litros por Día')
            plt.xlabel('Fecha')
            plt.ylabel('Litros Entregados')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Convertir gráfico a base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            grafico_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            plt.close()
            
            graficos["litros_por_dia"] = grafico_base64
        
        # Gráfico de distribución por gasolinera
        if "distribucion_por_gasolinera" in reporte["graficos"]:
            plt.figure(figsize=(12, 6))
            gasolineras = [item["nombre"] for item in reporte["graficos"]["distribucion_por_gasolinera"]]
            litros = [item["litros"] for item in reporte["graficos"]["distribucion_por_gasolinera"]]
            
            plt.bar(gasolineras, litros, color='#8BC34A')
            plt.title('Distribución de Litros por Gasolinera')
            plt.xlabel('Gasolinera')
            plt.ylabel('Litros Entregados')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Convertir gráfico a base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            grafico_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            plt.close()
            
            graficos["distribucion_por_gasolinera"] = grafico_base64
        
        # Gráfico comparativo (optimizado vs actual)
        if "comparativa" in reporte["graficos"]:
            plt.figure(figsize=(10, 6))
            conceptos = [item["concepto"] for item in reporte["graficos"]["comparativa"]]
            valores_opt = [item["optimizado"] for item in reporte["graficos"]["comparativa"]]
            valores_act = [item["actual"] for item in reporte["graficos"]["comparativa"]]
            
            x = range(len(conceptos))
            width = 0.35
            
            plt.bar([i - width/2 for i in x], valores_opt, width, label='Optimizado', color='#4CAF50')
            plt.bar([i + width/2 for i in x], valores_act, width, label='Actual', color='#FF9800')
            
            plt.title('Comparativa: Optimizado vs. Actual')
            plt.xlabel('Concepto')
            plt.ylabel('Valor (MXN)')
            plt.xticks(x, conceptos)
            plt.legend()
            plt.tight_layout()
            
            # Convertir gráfico a base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            grafico_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            plt.close()
            
            graficos["comparativa"] = grafico_base64
        
        return graficos
    
    def ejecutar_optimizacion(self, dias=7, gasolineras_seleccionadas=None):
        """Ejecuta el proceso completo de optimización y genera reportes"""
        # Si no se especifican gasolineras, usar todas
        if gasolineras_seleccionadas is None:
            gasolineras_seleccionadas = self.gasolineras
        else:
            # Convertir a enteros si vienen como strings
            gasolineras_seleccionadas = [int(g) if isinstance(g, str) else g for g in gasolineras_seleccionadas]
        
        # Filtrar las gasolineras válidas
        gasolineras_validas = [g for g in gasolineras_seleccionadas if g in self.gasolineras]
        
        if not gasolineras_validas:
            return {"error": "No se seleccionaron gasolineras válidas"}
        
        # Optimizar la distribución
        mejor_plan, fitness, historico = self.optimizar(dias, gasolineras_validas)
        
        # Generar reporte detallado
        reporte = self.generar_reporte(mejor_plan, dias)
        
        # Generar predicciones de demanda
        predicciones = self.generar_prediccion_demanda(gasolineras_validas, dias)
        
        # Generar gráficos
        graficos = self.generar_graficos_resultados(reporte)
        
        # Resultados finales
        resultado = {
            "fitness": fitness,
            "reporte": reporte,
            "predicciones": predicciones,
            "graficos": graficos
        }
        
        return resultado

# Interfaz de usuario
class OptimizadorGasolinaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Optimizador de Distribución de Gasolina")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f8f0")
        
        # Colores y estilos
        self.color_primario = "#4CAF50"  # Verde
        self.color_secundario = "#8BC34A"  # Verde claro
        self.color_fondo = "#f0f8f0"  # Verde muy claro
        self.color_acento = "#FF9800"  # Naranja
        
        # Estilos para ttk
        self.estilo = ttk.Style()
        self.estilo.theme_use('clam')
        self.estilo.configure('TFrame', background=self.color_fondo)
        self.estilo.configure('TLabel', background=self.color_fondo, font=('Helvetica', 10))
        self.estilo.configure('TButton', 
                             background=self.color_primario, 
                             foreground='white', 
                             font=('Helvetica', 10, 'bold'),
                             borderwidth=1)
        self.estilo.map('TButton', 
                       background=[('active', self.color_secundario)])
        self.estilo.configure('Header.TLabel', 
                             font=('Helvetica', 16, 'bold'), 
                             foreground=self.color_primario)
        self.estilo.configure('Subheader.TLabel', 
                             font=('Helvetica', 12, 'bold'), 
                             foreground=self.color_primario)
                             
        # Inicializar algoritmo
        try:
            self.algoritmo = AlgoritmoGeneticoGasolina()
            self.csv_cargado = True
        except Exception as e:
            self.csv_cargado = False
            messagebox.showerror("Error", f"Error al cargar datos: {str(e)}")
        
        # Crear panel principal
        self.crear_panel_principal()
        
    def crear_panel_principal(self):
        # Panel principal con pestañas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Pestaña de configuración
        self.tab_config = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_config, text="Configuración")
        
        # Pestaña de resultados
        self.tab_resultados = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_resultados, text="Resultados")
        
        # Pestaña de gráficos
        self.tab_graficos = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_graficos, text="Gráficos")
        
        # Pestaña de plan detallado
        self.tab_plan = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_plan, text="Plan Detallado")
        
        # Configurar pestaña de configuración
        self.configurar_tab_config()
        
    def configurar_tab_config(self):
        # Frame para CSV y parámetros
        frame_csv = ttk.Frame(self.tab_config)
        frame_csv.pack(fill=tk.X, padx=20, pady=10)
        
        # Título
        titulo = ttk.Label(frame_csv, text="Optimizador de Distribución de Gasolina", style="Header.TLabel")
        titulo.pack(pady=10)
        
        # Frame para cargar CSV
        frame_archivo = ttk.Frame(frame_csv)
        frame_archivo.pack(fill=tk.X, pady=10)
        
        ttk.Label(frame_archivo, text="Archivo de datos:").pack(side=tk.LEFT, padx=5)
        
        self.ruta_csv_var = tk.StringVar()
        self.ruta_csv_var.set("datos_gasolineras_tuxtla.csv" if self.csv_cargado else "")
        
        entry_csv = ttk.Entry(frame_archivo, textvariable=self.ruta_csv_var, width=50)
        entry_csv.pack(side=tk.LEFT, padx=5)
        
        btn_explorar = ttk.Button(frame_archivo, text="Explorar", command=self.seleccionar_archivo)
        btn_explorar.pack(side=tk.LEFT, padx=5)
        
        btn_cargar = ttk.Button(frame_archivo, text="Cargar Datos", command=self.cargar_datos)
        btn_cargar.pack(side=tk.LEFT, padx=5)
        
        # Frame para parámetros
        frame_parametros = ttk.LabelFrame(self.tab_config, text="Parámetros de Optimización")
        frame_parametros.pack(fill=tk.X, padx=20, pady=10)
        
        # Parámetro: Días
        frame_dias = ttk.Frame(frame_parametros)
        frame_dias.pack(fill=tk.X, pady=5)
        
        ttk.Label(frame_dias, text="Días a optimizar:").pack(side=tk.LEFT, padx=5)
        
        self.dias_var = tk.IntVar(value=7)
        dias_spinbox = ttk.Spinbox(frame_dias, from_=1, to=14, textvariable=self.dias_var, width=5)
        dias_spinbox.pack(side=tk.LEFT, padx=5)
        
        # Parámetro: Hora de inicio
        frame_hora = ttk.Frame(frame_parametros)
        frame_hora.pack(fill=tk.X, pady=5)
        
        ttk.Label(frame_hora, text="Rango horario de entregas:").pack(side=tk.LEFT, padx=5)
        
        self.hora_inicio_var = tk.IntVar(value=6)
        hora_inicio_spinbox = ttk.Spinbox(frame_hora, from_=0, to=23, textvariable=self.hora_inicio_var, width=5)
        hora_inicio_spinbox.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(frame_hora, text="a").pack(side=tk.LEFT, padx=5)
        
        self.hora_fin_var = tk.IntVar(value=18)
        hora_fin_spinbox = ttk.Spinbox(frame_hora, from_=0, to=23, textvariable=self.hora_fin_var, width=5)
        hora_fin_spinbox.pack(side=tk.LEFT, padx=5)
        
        # Frame para selección de gasolineras
        frame_gasolineras = ttk.LabelFrame(self.tab_config, text="Selección de Gasolineras")
        frame_gasolineras.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Lista de gasolineras
        frame_lista = ttk.Frame(frame_gasolineras)
        frame_lista.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Scrollbar para la lista
        scrollbar = ttk.Scrollbar(frame_lista)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Lista con checkboxes
        self.lista_gasolineras = tk.Listbox(frame_lista, selectmode=tk.MULTIPLE, 
                                          yscrollcommand=scrollbar.set, 
                                          height=15,
                                          bg="white",
                                          font=('Helvetica', 10))
        self.lista_gasolineras.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=self.lista_gasolineras.yview)
        
        # Botones de selección
        frame_botones_seleccion = ttk.Frame(frame_gasolineras)
        frame_botones_seleccion.pack(fill=tk.X, pady=5)
        
        btn_seleccionar_todo = ttk.Button(frame_botones_seleccion, text="Seleccionar Todo", 
                                        command=self.seleccionar_todas_gasolineras)
        btn_seleccionar_todo.pack(side=tk.LEFT, padx=5)
        
        btn_deseleccionar_todo = ttk.Button(frame_botones_seleccion, text="Deseleccionar Todo", 
                                          command=self.deseleccionar_todas_gasolineras)
        btn_deseleccionar_todo.pack(side=tk.LEFT, padx=5)
        
        # Botón para iniciar la optimización
        frame_optimizar = ttk.Frame(self.tab_config)
        frame_optimizar.pack(fill=tk.X, padx=20, pady=20)
        
        self.btn_optimizar = ttk.Button(frame_optimizar, text="INICIAR OPTIMIZACIÓN", 
                                      command=self.ejecutar_optimizacion,
                                      style='TButton')
        self.btn_optimizar.pack(pady=10, ipady=5, fill=tk.X)
        
        # Cargar la lista de gasolineras si hay datos
        if self.csv_cargado:
            self.cargar_lista_gasolineras()

    def seleccionar_archivo(self):
        ruta_archivo = filedialog.askopenfilename(
            title="Seleccionar archivo CSV",
            filetypes=[("Archivos CSV", ".csv"), ("Todos los archivos", ".*")]
        )
        
        if ruta_archivo:
            self.ruta_csv_var.set(ruta_archivo)
    
    def cargar_datos(self):
        ruta_csv = self.ruta_csv_var.get()
        
        if not os.path.exists(ruta_csv):
            messagebox.showerror("Error", f"El archivo {ruta_csv} no existe.")
            return
        
        try:
            self.algoritmo = AlgoritmoGeneticoGasolina(ruta_csv)
            self.csv_cargado = True
            messagebox.showinfo("Éxito", "Datos cargados correctamente.")
            self.cargar_lista_gasolineras()
        except Exception as e:
            self.csv_cargado = False
            messagebox.showerror("Error", f"Error al cargar los datos: {str(e)}")
    
    def cargar_lista_gasolineras(self):
        # Limpiar lista actual
        self.lista_gasolineras.delete(0, tk.END)
        
        # Agregar gasolineras a la lista
        for gid in self.algoritmo.gasolineras:
            nombre = self.algoritmo.nombres_gasolineras[gid]
            self.lista_gasolineras.insert(tk.END, f"{gid} - {nombre}")
    
    def seleccionar_todas_gasolineras(self):
        self.lista_gasolineras.select_set(0, tk.END)
    
    def deseleccionar_todas_gasolineras(self):
        self.lista_gasolineras.selection_clear(0, tk.END)
    
    def obtener_gasolineras_seleccionadas(self):
        indices = self.lista_gasolineras.curselection()
        gasolineras = []
        
        for idx in indices:
            texto = self.lista_gasolineras.get(idx)
            gid = int(texto.split(" - ")[0])
            gasolineras.append(gid)
        
        return gasolineras
    
    def ejecutar_optimizacion(self):
        if not self.csv_cargado:
            messagebox.showerror("Error", "Debe cargar datos primero.")
            return
        
        # Obtener parámetros
        dias = self.dias_var.get()
        gasolineras = self.obtener_gasolineras_seleccionadas()
        
        if not gasolineras:
            messagebox.showerror("Error", "Debe seleccionar al menos una gasolinera.")
            return
        
        # Mostrar mensaje de espera
        self.root.config(cursor="wait")
        self.btn_optimizar.config(state="disabled")
        self.root.update()
        
        try:
            # Ejecutar optimización
            self.resultado = self.algoritmo.ejecutar_optimizacion(dias, gasolineras)
            
            # Mostrar resultados
            self.mostrar_resultados()
            self.mostrar_graficos()
            self.mostrar_plan_detallado()
            
            # Cambiar a pestaña de resultados
            self.notebook.select(1)
            
            messagebox.showinfo("Éxito", "Optimización completada con éxito.")
        except Exception as e:
            messagebox.showerror("Error", f"Error durante la optimización: {str(e)}")
        finally:
            # Restaurar cursor y botón
            self.root.config(cursor="")
            self.btn_optimizar.config(state="normal")
    
    def mostrar_resultados(self):
        # Limpiar pestaña de resultados
        for widget in self.tab_resultados.winfo_children():
            widget.destroy()
        
        if not hasattr(self, 'resultado'):
            ttk.Label(self.tab_resultados, text="No hay resultados para mostrar.").pack(pady=20)
            return
        
        # Frame principal
        frame_principal = ttk.Frame(self.tab_resultados)
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Título
        ttk.Label(frame_principal, text="Resultados de la Optimización", style="Header.TLabel").pack(pady=10)
        
        # Métricas principales
        frame_metricas = ttk.LabelFrame(frame_principal, text="Métricas Principales")
        frame_metricas.pack(fill=tk.X, pady=10)
        
        # Grid para métricas
        for i, (metrica, valor) in enumerate([
            ("Fitness", f"{self.resultado['fitness']:.2f}"),
            ("Costo Total", f"${self.resultado['reporte']['metricas']['costo_total']:,.2f}"),
            ("Beneficio Total", f"${self.resultado['reporte']['metricas']['beneficio_total']:,.2f}"),
            ("Beneficio Neto", f"${self.resultado['reporte']['metricas']['beneficio_neto']:,.2f}"),
            ("Kilómetros Totales", f"{self.resultado['reporte']['metricas']['kilometros_totales']:,.2f} km"),
            ("Litros Entregados", f"{self.resultado['reporte']['metricas']['litros_entregados']:,} L"),
            ("Número de Rutas", f"{self.resultado['reporte']['metricas']['numero_rutas']}"),
            ("Costo por Litro", f"${self.resultado['reporte']['metricas']['costo_por_litro']:.2f}/L"),
            ("Rendimiento", f"{self.resultado['reporte']['metricas']['rendimiento']:.2f}")
        ]):
            ttk.Label(frame_metricas, text=metrica + ":", font=('Helvetica', 10, 'bold')).grid(row=i//3, column=(i%3)*2, sticky=tk.W, padx=10, pady=5)
            ttk.Label(frame_metricas, text=valor).grid(row=i//3, column=(i%3)*2+1, sticky=tk.W, padx=10, pady=5)
        
        # Comparación con sistema actual
        frame_comparacion = ttk.LabelFrame(frame_principal, text="Comparación con Sistema Actual")
        frame_comparacion.pack(fill=tk.X, pady=10)
        
        # Grid para comparación
        ttk.Label(frame_comparacion, text="Concepto", font=('Helvetica', 10, 'bold')).grid(row=0, column=0, padx=10, pady=5)
        ttk.Label(frame_comparacion, text="Sistema Actual", font=('Helvetica', 10, 'bold')).grid(row=0, column=1, padx=10, pady=5)
        ttk.Label(frame_comparacion, text="Sistema Optimizado", font=('Helvetica', 10, 'bold')).grid(row=0, column=2, padx=10, pady=5)
        ttk.Label(frame_comparacion, text="Diferencia", font=('Helvetica', 10, 'bold')).grid(row=0, column=3, padx=10, pady=5)
        
        # Datos de comparación
        comparacion = self.resultado['reporte']['comparacion']
        metricas = self.resultado['reporte']['metricas']
        
        # Fila: Costo
        ttk.Label(frame_comparacion, text="Costo").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        ttk.Label(frame_comparacion, text=f"${comparacion['costo_actual']:,.2f}").grid(row=1, column=1, padx=10, pady=5)
        ttk.Label(frame_comparacion, text=f"${metricas['costo_total']:,.2f}").grid(row=1, column=2, padx=10, pady=5)
        ttk.Label(frame_comparacion, text=f"-${comparacion['ahorro_costo']:,.2f}").grid(row=1, column=3, padx=10, pady=5)
        
        # Fila: Beneficio
        ttk.Label(frame_comparacion, text="Beneficio").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        ttk.Label(frame_comparacion, text=f"${comparacion['beneficio_actual']:,.2f}").grid(row=2, column=1, padx=10, pady=5)
        ttk.Label(frame_comparacion, text=f"${metricas['beneficio_total']:,.2f}").grid(row=2, column=2, padx=10, pady=5)
        ttk.Label(frame_comparacion, text=f"+${comparacion['incremento_beneficio']:,.2f}").grid(row=2, column=3, padx=10, pady=5)
        
        # Fila: Beneficio Neto
        ttk.Label(frame_comparacion, text="Beneficio Neto").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
        ttk.Label(frame_comparacion, text=f"${comparacion['beneficio_neto_actual']:,.2f}").grid(row=3, column=1, padx=10, pady=5)
        ttk.Label(frame_comparacion, text=f"${metricas['beneficio_neto']:,.2f}").grid(row=3, column=2, padx=10, pady=5)
        mejora_neta = metricas['beneficio_neto'] - comparacion['beneficio_neto_actual']
        ttk.Label(frame_comparacion, text=f"+${mejora_neta:,.2f}").grid(row=3, column=3, padx=10, pady=5)
        
        # Fila: Mejora Porcentual
        ttk.Label(frame_comparacion, text="Mejora Porcentual").grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
        ttk.Label(frame_comparacion, text="-").grid(row=4, column=1, padx=10, pady=5)
        ttk.Label(frame_comparacion, text="-").grid(row=4, column=2, padx=10, pady=5)
        ttk.Label(frame_comparacion, text=f"+{comparacion['mejora_porcentual']}%").grid(row=4, column=3, padx=10, pady=5)
    
    def mostrar_graficos(self):
        # Limpiar pestaña de gráficos
        for widget in self.tab_graficos.winfo_children():
            widget.destroy()
        
        if not hasattr(self, 'resultado'):
            ttk.Label(self.tab_graficos, text="No hay gráficos para mostrar.").pack(pady=20)
            return
        
        # Frame principal
        frame_principal = ttk.Frame(self.tab_graficos)
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Título
        ttk.Label(frame_principal, text="Gráficos de Resultados", style="Header.TLabel").pack(pady=10)
        
        # Frame para los gráficos
        frame_graficos = ttk.Frame(frame_principal)
        frame_graficos.pack(fill=tk.BOTH, expand=True)
        
        # Mostrar gráficos
        graficos = self.resultado["graficos"]
        
        # Gráfico 1: Distribución de litros por día
        if "litros_por_dia" in graficos:
            frame_g1 = ttk.LabelFrame(frame_graficos, text="Distribución de Litros por Día")
            frame_g1.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
            
            # Convertir base64 a imagen
            img_data = base64.b64decode(graficos["litros_por_dia"])
            img = Image.open(BytesIO(img_data))
            img_tk = ImageTk.PhotoImage(img)
            
            # Mostrar imagen
            label_img = ttk.Label(frame_g1, image=img_tk)
            label_img.image = img_tk  # Mantener referencia
            label_img.pack(padx=5, pady=5)
        
        # Gráfico 2: Distribución por gasolinera
        if "distribucion_por_gasolinera" in graficos:
            frame_g2 = ttk.LabelFrame(frame_graficos, text="Distribución de Litros por Gasolinera")
            frame_g2.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')
            
            # Convertir base64 a imagen
            img_data = base64.b64decode(graficos["distribucion_por_gasolinera"])
            img = Image.open(BytesIO(img_data))
            img_tk = ImageTk.PhotoImage(img)
            
            # Mostrar imagen
            label_img = ttk.Label(frame_g2, image=img_tk)
            label_img.image = img_tk  # Mantener referencia
            label_img.pack(padx=5, pady=5)
        
        # Gráfico 3: Comparativa
        if "comparativa" in graficos:
            frame_g3 = ttk.LabelFrame(frame_graficos, text="Comparativa: Optimizado vs. Actual")
            frame_g3.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')
            
            # Convertir base64 a imagen
            img_data = base64.b64decode(graficos["comparativa"])
            img = Image.open(BytesIO(img_data))
            img_tk = ImageTk.PhotoImage(img)
            
            # Mostrar imagen
            label_img = ttk.Label(frame_g3, image=img_tk)
            label_img.image = img_tk  # Mantener referencia
            label_img.pack(padx=5, pady=5)
        
        # Configurar el grid para que los gráficos ocupen el espacio disponible
        frame_graficos.grid_columnconfigure(0, weight=1)
        frame_graficos.grid_columnconfigure(1, weight=1)
        frame_graficos.grid_rowconfigure(0, weight=1)
        frame_graficos.grid_rowconfigure(1, weight=1)
    
    def mostrar_plan_detallado(self):
        # Limpiar pestaña de plan detallado
        for widget in self.tab_plan.winfo_children():
            widget.destroy()
        
        if not hasattr(self, 'resultado'):
            ttk.Label(self.tab_plan, text="No hay plan para mostrar.").pack(pady=20)
            return
        
        # Frame principal con scroll
        frame_canvas = ttk.Frame(self.tab_plan)
        frame_canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Agregar scrollbar
        vsb = ttk.Scrollbar(frame_canvas, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Crear canvas con scrollbar
        canvas = tk.Canvas(frame_canvas, yscrollcommand=vsb.set, background=self.color_fondo)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        vsb.config(command=canvas.yview)
        
        # Frame dentro del canvas para el contenido
        frame_contenido = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=frame_contenido, anchor="nw")
        
        # Título
        ttk.Label(frame_contenido, text="Plan Detallado de Distribución", style="Header.TLabel").pack(pady=10)
        
        # Mostrar plan por días
        plan = self.resultado["reporte"]["plan_distribucion"]
        
        for dia in plan:
            # Frame para el día
            frame_dia = ttk.LabelFrame(frame_contenido, text=f"Fecha: {dia['fecha']}")
            frame_dia.pack(fill=tk.X, pady=10)
            
            if not dia["rutas"]:
                ttk.Label(frame_dia, text="No hay rutas programadas para este día.").pack(pady=5)
                continue
            
            for ruta in dia["rutas"]:
                # Frame para la ruta
                frame_ruta = ttk.Frame(frame_dia)
                frame_ruta.pack(fill=tk.X, pady=5)
                
                # Encabezado de la ruta
                ttk.Label(frame_ruta, text=f"Ruta #{ruta['id_ruta']} - Salida: {ruta['hora_salida']}", 
                         style="Subheader.TLabel").pack(anchor="w")
                
                # Información general de la ruta
                info_ruta = f"Distancia total: {ruta['distancia_total']} km | " + \
                           f"Tiempo estimado: {ruta['tiempo_estimado']} horas | " + \
                           f"Costo: ${ruta['costo_transporte']:.2f} | " + \
                           f"Beneficio: ${ruta['beneficio']:.2f} | " + \
                           f"Litros totales: {ruta['litros_totales']} L"
                
                ttk.Label(frame_ruta, text=info_ruta).pack(anchor="w", padx=10)
                
                # Tabla de paradas
                frame_tabla = ttk.Frame(frame_ruta)
                frame_tabla.pack(fill=tk.X, padx=10, pady=5)
                
                # Encabezados de la tabla
                ttk.Label(frame_tabla, text="#", width=5).grid(row=0, column=0, padx=2, pady=2)
                ttk.Label(frame_tabla, text="Gasolinera", width=30).grid(row=0, column=1, padx=2, pady=2)
                ttk.Label(frame_tabla, text="Litros", width=10).grid(row=0, column=2, padx=2, pady=2)
                ttk.Label(frame_tabla, text="Hora de llegada", width=15).grid(row=0, column=3, padx=2, pady=2)
                ttk.Label(frame_tabla, text="Distancia", width=10).grid(row=0, column=4, padx=2, pady=2)
                
                # Filas de la tabla
                for i, parada in enumerate(ruta["paradas"]):
                    ttk.Label(frame_tabla, text=str(i+1)).grid(row=i+1, column=0, padx=2, pady=2)
                    ttk.Label(frame_tabla, text=parada["nombre"]).grid(row=i+1, column=1, padx=2, pady=2)
                    ttk.Label(frame_tabla, text=f"{parada['litros_entregados']} L").grid(row=i+1, column=2, padx=2, pady=2)
                    ttk.Label(frame_tabla, text=parada["hora_llegada"]).grid(row=i+1, column=3, padx=2, pady=2)
                    ttk.Label(frame_tabla, text=f"{parada['distancia_km']} km").grid(row=i+1, column=4, padx=2, pady=2)
        
        #scroll
        frame_contenido.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))


# Función principal
def main():
    root = tk.Tk()
    app = OptimizadorGasolinaGUI(root)
    root.mainloop()
    

if __name__ == "__main__":
    main()