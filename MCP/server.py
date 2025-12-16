from fastmcp import FastMCP
from routingpy import ORS
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from dotenv import load_dotenv
import os

load_dotenv()

# Вставьте ваш ключ
ORS_API_KEY=os.getenv("ORS_API_KEY")

# Инициализируем сервер и геокодер
mcp = FastMCP("Routing Demo Server")
geolocator = Nominatim(user_agent="my_mcp_server_tutorial")

@mcp.tool()
def get_coordinates(address: str) -> str:
    """
    Находит координаты (широту и долготу) по текстовому адресу.
    Пример: "Главный корпус ТГУ, Томск"
    """
    try:
        # Ищем адрес
        location = geolocator.geocode(address)
        if location:
            return f"Адрес: {location.address}\nКоординаты: {location.latitude}, {location.longitude}"
        else:
            return f"Не удалось найти адрес: {address}"
    except Exception as e:
        return f"Ошибка геокодирования: {e}"

@mcp.tool()
def get_route_by_address(start_address: str, end_address: str, profile: str = "driving-car") -> str:
    """
    Строит маршрут между двумя адресами (названиями мест).
    
    Args:
        start_address: Откуда едем (например, "Москва, Кремль")
        end_address: Куда едем (например, "Москва, Парк Горького")
        profile: Тип транспорта ('driving-car', 'foot-walking')
    """
    try:
        # 1. Находим координаты начала
        start_loc = geolocator.geocode(start_address)
        if not start_loc:
            return f"❌ Не найден начальный адрес: {start_address}"
            
        # 2. Находим координаты конца
        end_loc = geolocator.geocode(end_address)
        if not end_loc:
            return f"❌ Не найден конечный адрес: {end_address}"
            
        # 3. Строим маршрут (используя routingpy)
        client = ORS(api_key=ORS_API_KEY)
        
        # routingpy требует [LONGITUDE, LATITUDE]
        coords = [
            [start_loc.longitude, start_loc.latitude],
            [end_loc.longitude, end_loc.latitude]
        ]
        
        route = client.directions(locations=coords, profile=profile)
        
        distance_km = route.distance / 1000
        duration_min = route.duration / 60
        
        return (f"🚗 Маршрут: {start_loc.address} ➡️ {end_loc.address}\n"
                f"📏 Расстояние: {distance_km:.2f} км\n"
                f"⏱️ Время: {duration_min:.0f} мин")
                
    except Exception as e:
        return f"Ошибка при построении маршрута: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8000)
