from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from services.api_client import get_events, get_vacancies
from models import db, User, Participation

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

    # Забираем даты из запроса
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')

    # Передаем их в функцию
    events, total_pages = get_events(page, search_query, event_format, date_from, date_to)

    return render_template(
        'index.html',
        events=events,
        current_page=page,
        total_pages=total_pages,
        search_query=search_query,
        event_format=event_format,
        date_from=date_from,  # Отправляем в шаблон
        date_to=date_to  # Отправляем в шаблон
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
@login_required  # Добавили защиту
def profile():
    # Теперь берем не первого попавшегося, а ТЕКУЩЕГО пользователя!
    level = calculate_level(current_user.points)
    progress = current_user.points % 100
    return render_template('profile.html', user=current_user, level=level, progress=progress)


@app.route('/participate', methods=['POST'])
@login_required  # Добавили защиту
def participate():
    event_id = request.form.get('event_id')
    event_title = request.form.get('event_title')

    existing_entry = Participation.query.filter_by(user_id=current_user.id, event_id=event_id).first()

    if not existing_entry:
        new_participation = Participation(user_id=current_user.id, event_id=event_id, event_title=event_title)
        current_user.points += 50
        db.session.add(new_participation)
        db.session.commit()

    return redirect(url_for('profile'))

@app.route('/vacancies')
def vacancies():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '')
    salary_from = request.args.get('salary_from', '')

    # Запрашиваем вакансии через наш сервис
    vacancies_list, total_pages = get_vacancies(page, search_query, salary_from)

    return render_template(
        'vacancies.html',
        vacancies=vacancies_list,
        current_page=page,
        total_pages=total_pages,
        search_query=search_query,
        salary_from=salary_from
    )

if __name__ == '__main__':
    app.run(debug=True)