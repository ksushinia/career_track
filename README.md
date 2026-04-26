# Career Track

## About

Career Track is a web platform that connects **researchers / students** and **companies**.

Researchers can participate in scientific events, collect achievements, grow their profile, and find career opportunities.
Companies can publish vacancies, create events, and search for young talents.

---

## Main Features

### For Researchers

* Personal dashboard
* XP & level system
* Event participation tracking
* Favorite vacancies and events
* Public and internal events browsing
* Job search

### For Companies

* Company dashboard
* Vacancy creation and management
* Internal event publishing
* Talent search

### Platform Features

* Two user roles
* Gamification system
* External API integrations
* Search and filters
* Secure authentication

---

## Tech Stack

* Python
* Flask
* Flask-Login
* Flask-SQLAlchemy
* Pydantic
* SQLite

---

## Core Models

* `User`
* `Participation`
* `CompanyProfile`
* `InternalVacancy`
* `InternalEvent`
* `FavoriteEvent`
* `FavoriteVacancy`

---

## Main API Functions

* `get_events()`
* `get_event_detail()`
* `get_vacancies()`

---

## Installation

```bash id="v8j9c4"
git clone <repo_url>
cd project
pip install flask flask-login flask-sqlalchemy pydantic email-validator
python app.py
```

---

## Run Locally

Open:

```bash id="w7n2kl"
http://127.0.0.1:5000
```

---

## Goal

To turn academic activity and research achievements into real career opportunities.
