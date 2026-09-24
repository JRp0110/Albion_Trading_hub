# api_client.py
import requests
from config import BASE_URL

class AlbionApiClient:
    @staticmethod
    def fetch_market_data(items_list, locations_list, qualities="1,2,3,4,5"):
        """Consulta precios para una lista de ítems en ubicaciones y calidades específicas."""
        locations_str = ",".join(locations_list)
        resultados = []
        CHUNK_SIZE = 40  # Lotes seguros para evitar saturar la URL
        
        for i in range(0, len(items_list), CHUNK_SIZE):
            chunk = items_list[i:i + CHUNK_SIZE]
            items_str = ",".join(chunk)
            url = f"{BASE_URL}/{items_str}.json?locations={locations_str}&qualities={qualities}"
            
            try:
                response = requests.get(url, timeout=12)
                response.raise_for_status()
                resultados.extend(response.json())
            except requests.exceptions.RequestException as e:
                print(f"Error consultando API en bloque: {e}")
                
        return resultados