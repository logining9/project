from flask import Flask, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-me-in-production"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///shop.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"<User {self.username}>"


with app.app_context():
    db.create_all()


# ---------- Главная ----------
@app.route("/")
def index():
    return """
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Чекушников — сеть магазинов</title>
            <link rel="stylesheet" href="/static/style.css">
        </head>
        <body>
            <div class="hero">
                <div class="hero-card">
                    <h1 class="hero-title">
                        Чекушников
                        <span>Сеть магазинов</span>
                    </h1>
                    <p class="hero-subtitle">
                        Приветствуем на сайте сети магазинов «Чекушников»!
                        Всё необходимое — рядом с домом, по честным ценам
                        и без лишних хлопот.
                    </p>
                    <ul class="hero-features">
                        <li>Широкий ассортимент каждый день</li>
                        <li>Скидки по карте постоянного клиента</li>
                        <li>Заказ онлайн с самовывозом</li>
                    </ul>
                    <div class="hero-buttons">
                        <a href="/about" class="btn btn-outline">О нас</a>
                        <a href="/register" class="btn btn-primary">Зарегистрироваться</a>
                        <a href="/login" class="btn btn-ghost">Войти</a>
                    </div>
                </div>
            </div>
        </body>
        </html>
    """


# ---------- О нас ----------
@app.route("/about")
def about():
    return """
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>О нас — Чекушников</title>
            <link rel="stylesheet" href="/static/style.css">
        </head>
        <body>
            <div class="hero">
                <div class="hero-card about-card">
                    <a href="/" class="back-link">← На главную</a>
                    <h1 class="hero-title">О нас</h1>
                    <p class="hero-subtitle">
                        «Чекушников» — сеть магазинов у дома. Мы работаем, чтобы
                        нужные товары были рядом, по честным ценам и без лишних хлопот.
                    </p>
                    <div class="about-list">
                        <div class="about-item">
                            <span class="about-icon">🏪</span>
                            <div><h3>Кто мы</h3><p>Сеть магазинов «Чекушников» — широкий ассортимент каждый день и внимательные продавцы.</p></div>
                        </div>
                        <div class="about-item">
                            <span class="about-icon">💰</span>
                            <div><h3>Честные цены</h3><p>Доступные цены, регулярные акции и скидки по карте постоянного клиента.</p></div>
                        </div>
                        <div class="about-item">
                            <span class="about-icon">🛒</span>
                            <div><h3>Что у нас есть</h3><p>Продукты, напитки и товары первой необходимости — всё в одном месте.</p></div>
                        </div>
                        <div class="about-item">
                            <span class="about-icon">🚚</span>
                            <div><h3>Удобно</h3><p>Заказ онлайн с самовывозом из ближайшего магазина — без очередей.</p></div>
                        </div>
                    </div>
                    <div class="hero-buttons about-buttons">
                        <a href="/register" class="btn btn-primary">Зарегистрироваться</a>
                        <a href="/login" class="btn btn-ghost">Войти</a>
                    </div>
                </div>
            </div>
        </body>
        </html>
    """


# ---------- Регистрация (ГЛАВНОЕ ИСПРАВЛЕНИЕ) ----------
@app.route("/register", methods=["GET", "POST"])   # ← было без methods
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        password2 = request.form.get("password2", "")

        if not username or len(username) < 3:
            flash("Имя пользователя должно быть не короче 3 символов.", "danger")
        elif not email or "@" not in email:
            flash("Введите корректный email.", "danger")
        elif len(password) < 6:
            flash("Пароль должен быть не короче 6 символов.", "danger")
        elif password != password2:
            flash("Пароли не совпадают.", "danger")
        elif User.query.filter_by(email=email).first():
            flash("Пользователь с таким email уже существует.", "danger")
        elif User.query.filter_by(username=username).first():
            flash("Такое имя пользователя уже занято.", "danger")
        else:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash("Регистрация успешна! Теперь войдите.", "success")
            return redirect(url_for("login"))

    return """
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Регистрация — Чекушников</title>
            <link rel="stylesheet" href="/static/style.css">
        </head>
        <body>
            <div class="hero">
                <div class="hero-card form-card">
                    <a href="/" class="back-link">← На главную</a>
                    <h1 class="hero-title">Регистрация</h1>
                    <p class="hero-subtitle">
                        Создайте аккаунт «Чекушникова», чтобы заказывать товары
                        онлайн и получать скидки по карте постоянного клиента.
                    </p>

                    <form method="POST" action="/register" class="form" novalidate>
                        <div class="form-group">
                            <label for="username">Имя пользователя</label>
                            <input type="text" id="username" name="username"
                                placeholder="Например, ivan_petrov"
                                minlength="3" maxlength="50" required>
                        </div>
                        <div class="form-group">
                            <label for="email">Email</label>
                            <input type="email" id="email" name="email"
                                placeholder="you@example.com" required>
                        </div>
                        <div class="form-group">
                            <label for="password">Пароль</label>
                            <input type="password" id="password" name="password"
                                placeholder="Минимум 6 символов" minlength="6" required>
                        </div>
                        <div class="form-group">
                            <label for="password2">Повторите пароль</label>
                            <input type="password" id="password2" name="password2"
                                placeholder="Ещё раз" minlength="6" required>
                        </div>
                        <button type="submit" class="btn btn-primary btn-block">Создать аккаунт</button>
                    </form>

                    <p class="form-footer">
                        Уже есть аккаунт?
                        <a href="/login">Войти</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
    """


# ---------- Заглушка логина (чтобы redirect не падал) ----------
@app.route("/login")
def login():
    return """
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <title>Вход — Чекушников</title>
            <link rel="stylesheet" href="/static/style.css">
        </head>
        <body>
            <div class="hero">
                <div class="hero-card form-card">
                    <a href="/" class="back-link">← На главную</a>
                    <h1 class="hero-title">Вход</h1>
                    <p class="hero-subtitle">Страница входа скоро появится.</p>
                    <div class="hero-buttons">
                        <a href="/register" class="btn btn-primary">Зарегистрироваться</a>
                        <a href="/" class="btn btn-ghost">На главную</a>
                    </div>
                </div>
            </div>
        </body>
        </html>
    """


if __name__ == "__main__":
    app.run(debug=True)