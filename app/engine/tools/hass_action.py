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

HA_ACTION = Literal[
    "turn_on",
    "turn_off",
    "toggle",
    "set_cover_position",
    "open_cover",
    "close_cover",
    "stop_cover",
    "play_media",
    "pause",
    "media_play",
    "media_stop",
    "media_pause",
    "media_next_track",
    "media_previous_track",
    "volume_up",
    "volume_down",
    "play_media",
    "set_temperature",
    "value"
    # Añade aquí todas las acciones que necesites
]

class ParamsDict(TypedDict, total=False):
    """
    Definición de tipo para el diccionario de parámetros de la función 'run_hass_action'.
    total=False significa que no todas las claves son requeridas.
    """
    brightness: Optional[int]
    color_temp: Optional[int]
    color_temp_kelvin: Optional[int]
    rgb_color: Optional[list[int]]
    hs_color: Optional[list[float]]
    xy_color: Optional[list[float]]
    position: Optional[int]
    volume_level: Optional[float]
    media_content_id: Optional[str]
    media_content_type: Optional[str]
    temperature: Optional[str]
    # Puedes añadir más parámetros según necesites

class HassAction:
    @classmethod
    def run_hass_action(cls, entity_id: str, action: HA_ACTION, params: ParamsDict) -> str | None:
        """
        Ejecuta una acción (servicio) en Home Assistant.

        Args:
            entity_id (str): El ID de la entidad a la que aplicar la acción.
            action (str): El nombre de la acción (ej: "turn_on", "toggle").            
            params (dict, opcional): Un diccionario con parámetros adicionales para la acción.

        Returns:
            str o None: La respuesta de Home Assistant si la solicitud fue exitosa,
                        o None si hubo un error.
        """

        hassio_token = os.getenv('HASS_TOKEN')
        if not hassio_token:
            raise ValueError("HASS_TOKEN is not set in the environment variables")
        hassio_base_url = os.getenv('HASS_BASE_URL')
        if not hassio_base_url:
            raise ValueError("HASS_BASE_URL is not set in the environment variables")        

        headers = {
            "Authorization": f"Bearer {hassio_token}",
            "Content-Type": "application/json",
        }
        data = {
            "entity_id": entity_id,
            **params  # Añadir los parámetros adicionales
        }
        url = f"{hassio_base_url}/api/services/{entity_id.split('.')[0]}/{action}"

        try:
            response = requests.post(url, headers=headers, data=json.dumps(data), verify=False)
            response.raise_for_status()  # Lanza excepción para códigos de error HTTP (4xx, 5xx)

            if response.status_code == 200:
                return f"Acción {action} ejecutada correctamente en entidad {entity_id}. Action data: {data}"
            else:
                print(f"Error inesperado: Código de estado {response.status_code}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"Error de solicitud: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error al decodificar JSON: {e}")
            return None

def get_tools(**kwargs):
    return [FunctionTool.from_defaults(HassAction.run_hass_action)]
