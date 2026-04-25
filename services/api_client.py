import requests
import math
from config import Config


def get_events(page=1, search_query=None, event_format=None, date_from=None, date_to=None,
               event_type=None, age=None, category=None):
    url = f"{Config.API_BASE_URL}/event/"

    # Словарь для поиска по внешнему API (т.к. там нет поля "категория")
    category_map = {
        'IT и Data Science': 'IT',
        'Биомед': 'Медицина',
        'Физмат и Инженерия': 'Технические',
        'Экономика': 'Экономика',
        'Гуманитарные и общие': 'Гуманитарные'
    }

    params = {
        "page": page,
        "pageSize": 12,
        "isPublished": True,
        "sort": "-createdAt",
    }

    # Если пользователь выбрал категорию, добавляем её к поиску
    # Чтобы внешнее API выдало хоть что-то подходящее
    final_search = search_query or ""
    if category in category_map:
        keyword = category_map[category]
        if final_search:
            final_search = f"{final_search} {keyword}"
        else:
            final_search = keyword

    if final_search:
        params["search"] = final_search

    # Важно: API ПНВШ принимает только mixed, offline, online
    if event_format in ['offline', 'online', 'mixed']:
        params["eventFormat"] = event_format

    # Возраст
    if age:
        params["membersAgesMin"] = age
        params["membersAgesMax"] = age

    # Даты проведения (API требует формат ISO с временем)
    if date_from: params["periodsAfter"] = f"{date_from}T00:00:00"
    if date_to: params["periodsBefore"] = f"{date_to}T23:59:59"

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get('results', []), math.ceil(data.get('count', 0) / 12)
    except Exception as e:
        print(f"Ошибка API (events): {e}")
        return [], 1

def get_event_detail(event_id):
    """ПОЛУЧЕНИЕ ДЕТАЛЕЙ МЕРОПРИЯТИЯ """
    url = f"{Config.API_BASE_URL}/event/{event_id}/"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Ошибка API (event detail): {e}")
        return None

def get_vacancies(page=1, search_query=None, salary_from=None, salary_to=None, experience_id=None, schedule_id=None):
    url = f"{Config.API_BASE_URL}/vacancy/"
    params = {
        "page": page,
        "pageSize": 12,
        "sort": "-createdAt"
    }

    if search_query and search_query.strip():
        params["search"] = search_query.strip()

    if salary_from: params["salaryFrom"] = salary_from
    if salary_to: params["salaryUpTo"] = salary_to

    # API ПНВШ ожидает ID для опыта и графиков (передаем как массив, если нужно)
    if experience_id: params["experience"] = [experience_id]
    if schedule_id: params["schedule"] = [schedule_id]

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get('results', []), math.ceil(data.get('count', 0) / 12)
    except Exception as e:
        print(f"Ошибка API: {e}")
        return [], 1