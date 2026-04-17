from flask import Flask, render_template
from services.api_client import get_events

app = Flask(__name__)

# Для MVP сделаем "фейковую" базу данных пользователя в виде словаря.
# Позже ты заменишь это на SQLite или PostgreSQL
mock_user = {
    "name": "Ксения",
    "status": "Студент",
    "points": 350,
    "attended_events":[
        "Конференция молодых ученых 2025",
        "Хакатон IT-Science"
    ]
}

# Считаем уровень (например, каждые 100 баллов = 1 уровень)
def calculate_level(points):
    return (points // 100) + 1

@app.route('/')
def index():
    # Получаем реальные данные с портала науки
    events = get_events()
    return render_template('index.html', events=events)

@app.route('/profile')
def profile():
    # Передаем данные пользователя и рассчитываем его уровень
    level = calculate_level(mock_user["points"])
    # Прогресс до следующего уровня (в процентах от 0 до 100)
    progress = mock_user["points"] % 100
    return render_template('profile.html', user=mock_user, level=level, progress=progress)

if __name__ == '__main__':
    app.run(debug=True)