from flask import Flask, request, redirect, url_for, flash, session, render_template_string
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

class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(255), nullable=True) # Ссылка на картинку
    stock = db.Column(db.Integer, default=10) # Количество на складе

    def __repr__(self):
        return f"<Product {self.title}>"

with app.app_context():
    db.create_all()

    if not Product.query.first():
        test_products = [
            Product(title="Чекушка классическая", description="0.25 л, классическая рецептура.", price=250.0, image_url="https://via.placeholder.com/150"),
            Product(title="Пивной набор 'Пятница'", description="6 видов крафтового пива.", price=850.0, image_url="https://via.placeholder.com/150"),
            Product(title="Закуска к столу", description="Соленые орешки и чипсы.", price=120.0, image_url="https://via.placeholder.com/150"),
            Product(title="Напиток 'Бодрость'", description="Энергетик для бодрого утра.", price=99.0, image_url="https://via.placeholder.com/150"),
        ]
        db.session.add_all(test_products)
        db.session.commit()


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


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session["user_id"] = user.id
            session["username"] = user.username
            flash(f"С возвращением, {user.username}!", "success")
            return redirect(url_for("catalog"))
        else:
            flash("Неверный email или пароль.", "danger")

    return """
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Вход — Чекушников</title>
            <link rel="stylesheet" href="/static/style.css">
        </head>
        <body>
            <div class="hero">
                <div class="hero-card form-card">
                    <a href="/" class="back-link">← На главную</a>

                    <h1 class="hero-title">Вход</h1>
                    <p class="hero-subtitle">Войдите в аккаунт «Чекушникова», чтобы управлять заказами.</p>

                    <form method="POST" action="/login" class="form" novalidate>
                        <div class="form-group">
                            <label for="email">Email</label>
                            <input type="email" id="email" name="email"
                                placeholder="you@example.com" required>
                        </div>

                        <div class="form-group">
                            <label for="password">Пароль</label>
                            <input type="password" id="password" name="password"
                                placeholder="Ваш пароль" required>
                        </div>

                        <button type="submit" class="btn btn-primary btn-block">Войти</button>
                    </form>

                    <p class="form-footer">
                        Нет аккаунта?
                        <a href="/register">Зарегистрироваться</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
    """

@app.route("/catalog")
def catalog():
    # Получаем все товары из базы
    products = Product.query.all()
    
    # Передаем их в шаблон через render_template_string
    return render_template_string("""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Каталог — Чекушников</title>
            <link rel="stylesheet" href="/static/style.css">
        </head>
        <body>
            <div class="hero" style="align-items: flex-start; padding-top: 40px;">
                <div class="hero-card" style="max-width: 900px; text-align: left;">
                    
                    <!-- Шапка каталога -->
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                        <a href="/" class="back-link" style="margin: 0;">← На главную</a>
                        {% if session.get('user_id') %}
                            <span style="font-size: 0.9rem; color: #d32f2f; font-weight: bold;">Вы вошли как: {{ session.get('username') }}</span>
                        {% else %}
                            <a href="/login" style="font-size: 0.9rem; color: #d32f2f;">Войти</a>
                        {% endif %}
                    </div>

                    <h1 class="hero-title">Каталог товаров</h1>
                    <p class="hero-subtitle">Всё необходимое для отличного вечера.</p>

                    <!-- Сетка товаров -->
                    <div class="product-grid">
                        {% for p in products %}
                            <div class="product-card">
                                <img src="{{ p.image_url }}" alt="{{ p.title }}" class="product-image">
                                <h3 class="product-title">{{ p.title }}</h3>
                                <p class="product-desc">{{ p.description }}</p>
                                <div class="product-bottom">
                                    <span class="product-price">{{ p.price }} ₽</span>
                                    <button class="btn btn-primary" style="padding: 8px 16px; font-size: 0.9rem;">Купить</button>
                                </div>
                            </div>
                        {% else %}
                            <p>Товаров пока нет.</p>
                        {% endfor %}
                    </div>

                </div>
            </div>
        </body>
        </html>
    """, products=products)

if __name__ == "__main__":
    app.run(debug=True)