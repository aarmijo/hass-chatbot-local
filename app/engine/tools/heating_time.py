"""Home Assistant Action Tool spec."""
import logging
import os
import requests  # type: ignore
import json
from llama_index.core.tools import FunctionTool
from dotenv import load_dotenv
from typing_extensions import TypedDict, Optional
from typing_extensions import Literal

load_dotenv()

logger = logging.getLogger(__name__)

class HeatingFunction:
    @classmethod
    def calculate_thermal_capacity(cls, temperatura_inicial: float, temperatura_final: float, temperatura_exterior: float, duracion_horas: float,
                                area_vivienda: float, u_promedio: float) -> float:
        """
        Calcula la capacidad térmica total de la vivienda (aire + materiales) basada en observaciones experimentales.

        Args:
            temperatura_inicial (float): Temperatura inicial en ºC.
            temperatura_final (float): Temperatura final en ºC.
            temperatura_exterior (float): Temperatura exterior promedio en ºC.
            duracion_horas (float): Duración del periodo de observación en horas.
            area_vivienda (float): Superficie útil de la vivienda en m². Por defecto 90.
            u_promedio (float): Transmitancia térmica promedio de la vivienda en W/(m²·K). Por defecto 0.45.

        Returns:
            float: Capacidad térmica total de la vivienda en J/K.
        """

        # Ajuste del área envolvente al 80% del área de la vivienda para considerar más factores de pérdida
        area_envolvente = 0.8 * area_vivienda
        q_perdida = u_promedio * area_envolvente * (temperatura_inicial - temperatura_exterior) * duracion_horas * 3600

        delta_temperatura = temperatura_inicial - temperatura_final
        capacidad_termica_total = q_perdida / delta_temperatura

        return capacidad_termica_total

    @classmethod
    def calculate_heating_time(cls, temperatura_exterior: float, temperatura_interior_actual: float, temperatura_consigna: float = 21) -> str:
        """
        Calcula el tiempo de calefacción necesario para alcanzar una temperatura objetivo.

        Args:
            temperatura_exterior (float): Temperatura exterior actual en ºC.
            temperatura_interior_actual (float): Temperatura interior actual en ºC.
            temperatura_consigna (float, optional): Temperatura de confort interior en ºC. Por defecto 21.

        Returns:
            str: Tiempo de calefacción en horas.
        """

        # Parámetros fijos
        area_vivienda = 90  # Superficie útil de la vivienda en m²
        u_promedio = 0.45  # Transmitancia térmica promedio de la vivienda en W/(m²·K)
        potencia_caldera = 3500  # Potencia máxima de la caldera en W
        eficiencia_caldera = 0.9  # Eficiencia del sistema de calefacción (0 a 1)
        factor_pid = 0.8 # Factor de ajuste para el termostato PID (0 a 1). Por defecto 0.8.

        # Ajuste del área envolvente al 80% del área de la vivienda para considerar más factores de pérdida
        area_envolvente = 0.8 * area_vivienda
        q_perdida = u_promedio * area_envolvente * (temperatura_consigna - temperatura_exterior)
        q_ganancia_caldera = potencia_caldera * eficiencia_caldera * factor_pid

        delta_temperatura = temperatura_consigna - temperatura_interior_actual

        # Datos experimentales para calcular la capacidad térmica
        temperatura_inicial = 20.3
        temperatura_final = 18.91
        temperatura_exterior_promedio = 10
        duracion_horas = 13.5

        capacidad_termica_total = cls.calculate_thermal_capacity(temperatura_inicial, temperatura_final, temperatura_exterior_promedio, duracion_horas, area_vivienda, u_promedio)
        energia_necesaria_total = capacidad_termica_total * delta_temperatura

        if temperatura_interior_actual >= temperatura_consigna:
            tiempo_calefaccion = 0
        else:
            # Tiempo para calentar el aire y los materiales + tiempo para compensar las pérdidas
            tiempo_calefaccion = (energia_necesaria_total + q_perdida * 3600) / q_ganancia_caldera

        tiempo_calefaccion = tiempo_calefaccion / 3600  # Conversión a horas
        if tiempo_calefaccion == 0:
            return f"No es necesario activar la calefacción, ya que la temperatura actual ({temperatura_interior_actual}ºC) es superior o igual a la temperatura objetivo ({temperatura_consigna}ºC)"
        else:
            return f"El tiempo necesario de calefacción para alcanzar {temperatura_consigna}ºC con una temperatura interior de {temperatura_interior_actual}ºC y una exterior de {temperatura_exterior}ºC es de {tiempo_calefaccion:.2f} horas"

def get_tools(**kwargs):
    return [FunctionTool.from_defaults(HeatingFunction.calculate_heating_time)]
