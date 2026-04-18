from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from services.api_client import get_events, get_vacancies
from models import db, User, Participation, FavoriteEvent, FavoriteVacancy
from collections import Counter # Понадобится для радара
import json # Понадобится для передачи данных в JS

app = Flask(__name__)

# СЕКРЕТНЫЙ КЛЮЧ (Нужен для работы авторизации и сессий)
app.config['SECRET_KEY'] = 'super-secret-key-123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///career_track.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Настройка LoginManager
login_manager = LoginManager()
login_manager.login_view = 'login'  # Куда отправлять неавторизованных
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    db.create_all()


def calculate_level(points):
    return (points // 100) + 1


@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '')
    event_format = request.args.get('format', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')

    events, total_pages = get_events(page, search_query, event_format, date_from, date_to)

    # Получаем ID избранных мероприятий текущего юзера
    fav_event_ids =[]
    if current_user.is_authenticated:
        fav_event_ids =[f.event_id for f in FavoriteEvent.query.filter_by(user_id=current_user.id).all()]

    return render_template(
        'index.html',
        events=events, current_page=page, total_pages=total_pages,
        search_query=search_query, event_format=event_format,
        date_from=date_from, date_to=date_to,
        fav_event_ids=fav_event_ids # Передаем в шаблон
    )

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        name = request.form.get('name')
        password = request.form.get('password')

        # Проверка, есть ли такой логин
        if User.query.filter_by(username=username).first():
            flash('Этот логин уже занят!')
            return redirect(url_for('register'))

        # Создаем пользователя, шифруя пароль
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, name=name, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        # Сразу логиним его после регистрации
        login_user(new_user)
        return redirect(url_for('profile'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        # Проверяем пароль
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('profile'))
        else:
            flash('Неверный логин или пароль!')

    return render_template('login.html')


@app.route('/logout')
@login_required  # Доступно только авторизованным
def logout():
    logout_user()
    return redirect(url_for('index'))


# --- ОБНОВЛЕННЫЕ СТАРЫЕ МАРШРУТЫ ---

@app.route('/profile')
@login_required
def profile():
    level = calculate_level(current_user.points)
    progress = current_user.points % 100

    # ЛОГИКА ДЛЯ РАДАРА КОМПЕТЕНЦИЙ
    participations = Participation.query.filter_by(user_id=current_user.id).all()
    categories = [p.category for p in participations if p.category]
    counts = Counter(categories)

    # Базовые направления (чтобы график рисовался ровно, даже если там 0)
    base_categories = ['IT и Data Science', 'Биомед', 'Физмат и Инженерия', 'Экономика', 'Гуманитарные и общие']
    radar_data = [counts.get(cat, 0) for cat in base_categories]

    return render_template(
        'profile.html',
        user=current_user, level=level, progress=progress,
        radar_labels=json.dumps(base_categories),
        radar_data=json.dumps(radar_data)
    )


@app.route('/participate', methods=['POST'])
@login_required
def participate():
    event_id = request.form.get('event_id')
    event_title = request.form.get('event_title')

    existing_entry = Participation.query.filter_by(user_id=current_user.id, event_id=event_id).first()

    if not existing_entry:
        # Простенький алгоритм определения компетенции по названию (для MVP)
        title_lower = event_title.lower()
        if any(w in title_lower for w in ['информ', 'ит', 'it', 'данн', 'нейро', 'программ', 'ии']):
            cat = 'IT и Data Science'
        elif any(w in title_lower for w in ['мед', 'био', 'ген', 'здоров']):
            cat = 'Биомед'
        elif any(w in title_lower for w in ['физ', 'мат', 'инженер', 'техн', 'космос']):
            cat = 'Физмат и Инженерия'
        elif any(w in title_lower for w in ['эконом', 'менедж', 'бизнес', 'маркет']):
            cat = 'Экономика'
        else:
            cat = 'Гуманитарные и общие'

        new_participation = Participation(user_id=current_user.id, event_id=event_id, event_title=event_title,
                                          category=cat)
        current_user.points += 50
        db.session.add(new_participation)
        db.session.commit()

    return redirect(request.referrer or url_for('index'))  # Возвращает туда, откуда нажали


# --- РОУТЫ ИЗБРАННОГО ---
@app.route('/toggle_fav_event', methods=['POST'])
@login_required
def toggle_fav_event():
    event_id = request.form.get('event_id')
    event_title = request.form.get('event_title')

    fav = FavoriteEvent.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    if fav:
        db.session.delete(fav)  # Если есть - удаляем
    else:
        new_fav = FavoriteEvent(user_id=current_user.id, event_id=event_id, event_title=event_title)
        db.session.add(new_fav)  # Если нет - добавляем
    db.session.commit()
    return redirect(request.referrer or url_for('index'))


@app.route('/toggle_fav_vacancy', methods=['POST'])
@login_required
def toggle_fav_vacancy():
    vacancy_id = request.form.get('vacancy_id')
    vacancy_title = request.form.get('vacancy_title')
    hh_url = request.form.get('hh_url')

    fav = FavoriteVacancy.query.filter_by(user_id=current_user.id, vacancy_id=vacancy_id).first()
    if fav:
        db.session.delete(fav)
    else:
        new_fav = FavoriteVacancy(user_id=current_user.id, vacancy_id=vacancy_id, vacancy_title=vacancy_title,
                                  hh_url=hh_url)
        db.session.add(new_fav)
    db.session.commit()
    return redirect(request.referrer or url_for('vacancies'))

@app.route('/vacancies')
def vacancies():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '')
    salary_from = request.args.get('salary_from', '')

    vacancies_list, total_pages = get_vacancies(page, search_query, salary_from)

    # Получаем ID избранных вакансий
    fav_vacancy_ids =[]
    if current_user.is_authenticated:
        fav_vacancy_ids =[f.vacancy_id for f in FavoriteVacancy.query.filter_by(user_id=current_user.id).all()]

    return render_template(
        'vacancies.html',
        vacancies=vacancies_list, current_page=page, total_pages=total_pages,
        search_query=search_query, salary_from=salary_from,
        fav_vacancy_ids=fav_vacancy_ids # Передаем в шаблон
    )

if __name__ == '__main__':
    app.run(debug=True)