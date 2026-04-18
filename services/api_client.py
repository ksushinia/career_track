import requests
import math
from config import Config


def get_events(page=1, search_query=None, event_format=None, date_from=None, date_to=None):
    """Получает список мероприятий с учетом всех фильтров"""
    url = f"{Config.API_BASE_URL}/event/"
    params = {
        "page": page,
        "pageSize": 12,
        "isPublished": True,
        "sort": "-createdAt",
    }

    if search_query:
        params["search"] = search_query
    if event_format:
        params["eventFormat"] = event_format

    # Добавляем фильтры по датам (API требует формат date-time, поэтому добавляем время)
    if date_from:
        params["periodsAfter"] = f"{date_from}T00:00:00"
    if date_to:
        params["periodsBefore"] = f"{date_to}T23:59:59"

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        events = data.get('results', [])
        total_count = data.get('count', 0)

        total_pages = math.ceil(total_count / 12) if total_count > 0 else 1
        return events, total_pages
    except Exception as e:
        print(f"Ошибка при запросе к API: {e}")
        return [], 1

def get_vacancies(page=1, search_query=None, salary_from=None):
    """Получает список вакансий с учетом фильтров"""
    url = f"{Config.API_BASE_URL}/vacancy/"
    params = {
        "page": page,
        "pageSize": 12,
        "sort": "-createdAt",  # Сначала самые новые
    }

    if search_query:
        params["search"] = search_query
    if salary_from:
        params["salaryFrom"] = salary_from

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        vacancies = data.get('results',[])
        total_count = data.get('count', 0)

        total_pages = math.ceil(total_count / 12) if total_count > 0 else 1
        return vacancies, total_pages
    except Exception as e:
        print(f"Ошибка при запросе вакансий к API: {e}")
        return[], 1