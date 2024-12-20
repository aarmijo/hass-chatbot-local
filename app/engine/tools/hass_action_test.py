import requests
import json

def ejecutar_accion_hass(token, dominio, accion, entity_id, base_url="http://localhost:8123", params={}):
    """
    Ejecuta una acción (servicio) en Home Assistant.

    Args:
        token (str): El token de acceso de larga duración de Home Assistant.
        dominio (str): El dominio de la acción (ej: "switch", "light").
        servicio (str): El nombre de la acción (ej: "turn_on", "toggle").
        entity_id (str): El ID de la entidad a la que aplicar la acción.
        base_url (str, opcional): La URL base de Home Assistant. Por defecto es "http://localhost:8123".
        params (dict, opcional): Un diccionario con parámetros adicionales para la acción.

    Returns:
        dict o None: La respuesta JSON de Home Assistant si la solicitud fue exitosa,
                     o None si hubo un error.
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    data = {
        "entity_id": entity_id,
        **params  # Añadir los parámetros adicionales
    }
    url = f"{base_url}/api/services/{dominio}/{accion}"

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), verify=False)
        response.raise_for_status()  # Lanza excepción para códigos de error HTTP (4xx, 5xx)

        if response.status_code == 200:
            return f"Acción {accion} ejecutada correctamente en entidad {entity_id}. Action data: {data}"
        else:
            print(f"Error inesperado: Código de estado {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error de solicitud: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error al decodificar JSON: {e}")
        return None


if __name__ == '__main__':
    
    BASE_URL = "http://localhost:8123"
    # Reemplaza con tu token, dominio, acción y entity_id reales
    TOKEN_HASS = ""

    # Ejemplo para una luz (brillo y color)
    DOMINIO_EJEMPLO_LUZ = "light"
    ACCION_EJEMPLO_LUZ = "turn_on"
    ENTITY_ID_EJEMPLO_LUZ = "light.bombilla_lampara_de_techo"
    PARAMETROS_LUZ = {
        "entity_id": "light.bombilla_lampara_de_techo",
        "brightness": 200,
        "color_temp_kelvin": 3000
    }

    resultado = ejecutar_accion_hass(
        TOKEN_HASS, DOMINIO_EJEMPLO_LUZ, ACCION_EJEMPLO_LUZ, ENTITY_ID_EJEMPLO_LUZ, BASE_URL, params=PARAMETROS_LUZ)
    if resultado:
        print("Acción ejecutada con éxito.")
        print("Respuesta del servidor:", resultado)
    else:
        print("La ejecución de la acción falló.")
