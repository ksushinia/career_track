import requests
from config import Config

def get_events(page=1):
    """Получает список мероприятий с портала ПНВШ"""
    url = f"{Config.API_BASE_URL}/event/"
    params = {
        "page": page,
        "pageSize": 10,  # Забираем по 10 штук для MVP
        "isPublished": True
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get('results',[])
    except Exception as e:
        print(f"Ошибка при запросе к API: {e}")
        return[]