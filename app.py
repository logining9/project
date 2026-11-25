from flask import Flask, request, redirect, url_for, flash, session, render_template_string
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-me-in-production"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///shop.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


# ---------- МОДЕЛИ БАЗЫ ДАННЫХ ----------
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)

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
    image_url = db.Column(db.String(255), nullable=True)
    stock = db.Column(db.Integer, default=10)

    def __repr__(self):
        return f"<Product {self.title}>"


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    street = db.Column(db.String(150), nullable=False)
    house = db.Column(db.String(20), nullable=False)
    apartment = db.Column(db.String(20), nullable=False)
    entrance = db.Column(db.String(20), nullable=True)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='orders')


# ---------- ИНИЦИАЛИЗАЦИЯ БАЗЫ ----------
with app.app_context():
    db.create_all()

    if not User.query.filter_by(email="admin@chekushnikov.ru").first():
        admin = User(username="admin", email="admin@chekushnikov.ru", is_admin=True)
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()

    if not Product.query.first():
        test_products = [
            Product(title="Чекушка классическая", description="0.25 л, классическая рецептура.", price=250.0, image_url="chekushka.jpg"),
            Product(title="Пивной набор 'Пятница'", description="6 видов крафтового пива.", price=850.0, image_url="chekushka.jpg"),
            Product(title="Закуска к столу", description="Соленые орешки и чипсы.", price=120.0, image_url="chekushka.jpg"),
            Product(title="Напиток 'Бодрость'", description="Энергетик для бодрого утра.", price=99.0, image_url="chekushka.jpg"),
        ]
        db.session.add_all(test_products)
        db.session.commit()


# ---------- МАРШРУТЫ ----------
@app.route("/")
def index():
    return render_template_string("""
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
                        {% if session.get('user_id') %}
                            <a href="/catalog" class="btn btn-primary">Перейти в каталог</a>
                            <a href="/delivery" class="btn btn-outline">Доставка</a>
                            <a href="/logout" class="btn btn-ghost">Выйти</a>
                        {% else %}
                            <a href="/about" class="btn btn-outline">О нас</a>
                            <a href="/register" class="btn btn-primary">Зарегистрироваться</a>
                            <a href="/login" class="btn btn-ghost">Войти</a>
                        {% endif %}
                    </div>
                </div>
            </div>
        </body>
        </html>
    """)


@app.route("/about")
def about():
    return render_template_string("""
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
    """)


@app.route("/register", methods=["GET", "POST"])
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

    return render_template_string("""
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

                    {% with messages = get_flashed_messages(with_categories=true) %}
                        {% if messages %}
                            {% for category, message in messages %}
                                <div class="alert alert-{{ category }}">{{ message }}</div>
                            {% endfor %}
                        {% endif %}
                    {% endwith %}

                    <form method="POST" action="/register" class="form" novalidate>
                        <div class="form-group">
                            <label for="username">Имя пользователя</label>
                            <input type="text" id="username" name="username" placeholder="Например, ivan_petrov" minlength="3" maxlength="50" required>
                        </div>
                        <div class="form-group">
                            <label for="email">Email</label>
                            <input type="email" id="email" name="email" placeholder="you@example.com" required>
                        </div>
                        <div class="form-group">
                            <label for="password">Пароль</label>
                            <input type="password" id="password" name="password" placeholder="Минимум 6 символов" minlength="6" required>
                        </div>
                        <div class="form-group">
                            <label for="password2">Повторите пароль</label>
                            <input type="password" id="password2" name="password2" placeholder="Ещё раз" minlength="6" required>
                        </div>
                        <button type="submit" class="btn btn-primary btn-block">Создать аккаунт</button>
                    </form>

                    <p class="form-footer">
                        Уже есть аккаунт? <a href="/login">Войти</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
    """)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session["user_id"] = user.id
            session["username"] = user.username
            
            # Проверка на админа
            if user.is_admin:
                return redirect(url_for("admin_orders"))
            return redirect(url_for("catalog"))
        else:
            flash("Неверный email или пароль.", "danger")

    return render_template_string("""
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

                    {% with messages = get_flashed_messages(with_categories=true) %}
                        {% if messages %}
                            {% for category, message in messages %}
                                <div class="alert alert-{{ category }}">{{ message }}</div>
                            {% endfor %}
                        {% endif %}
                    {% endwith %}

                    <form method="POST" action="/login" class="form" novalidate>
                        <div class="form-group">
                            <label for="email">Email</label>
                            <input type="email" id="email" name="email" placeholder="you@example.com" required>
                        </div>
                        <div class="form-group">
                            <label for="password">Пароль</label>
                            <input type="password" id="password" name="password" placeholder="Ваш пароль" required>
                        </div>
                        <button type="submit" class="btn btn-primary btn-block">Войти</button>
                    </form>

                    <p class="form-footer">
                        Нет аккаунта? <a href="/register">Зарегистрироваться</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
    """)


@app.route("/catalog")
def catalog():
    products = Product.query.all()
    
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
                    
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 10px;">
                        <a href="/" class="back-link" style="margin: 0;">← На главную</a>
                        
                        <div style="display: flex; gap: 15px; align-items: center;">
                            <!-- Кнопка "Доставка" убрана отсюда -->
                            <a href="/cart" class="back-link" style="margin: 0;">Корзина ({{ session.get('cart', {})|length }})</a>
                            {% if session.get('user_id') %}
                                <a href="/my-orders" class="back-link" style="margin: 0;">Мои заказы</a>
                                <span style="font-size: 0.9rem; color: #d32f2f; font-weight: bold;">{{ session.get('username') }}</span>
                                <a href="/logout" style="font-size: 0.9rem; color: #888;">Выйти</a>
                            {% else %}
                                <a href="/login" style="font-size: 0.9rem; color: #d32f2f;">Войти</a>
                            {% endif %}
                        </div>
                    </div>

                    <h1 class="hero-title">Каталог товаров</h1>
                    <p class="hero-subtitle">Всё необходимое для отличного вечера.</p>

                    {% with messages = get_flashed_messages(with_categories=true) %}
                        {% if messages %}
                            {% for category, message in messages %}
                                <div class="alert alert-{{ category }}">{{ message }}</div>
                            {% endfor %}
                        {% endif %}
                    {% endwith %}

                    <div class="product-grid">
                        {% for p in products %}
                            <div class="product-card">
                                <img src="{{ url_for('static', filename='images/' + p.image_url) }}" alt="{{ p.title }}" class="product-image">
                                <h3 class="product-title">{{ p.title }}</h3>
                                <p class="product-desc">{{ p.description }}</p>
                                <div class="product-bottom">
                                    <span class="product-price">{{ p.price }} ₽</span>
                                    <a href="{{ url_for('add_to_cart', product_id=p.id) }}" class="btn btn-primary" style="padding: 8px 16px; font-size: 0.9rem; text-decoration: none;">Купить</a>
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


@app.route("/cart")
def cart():
    cart_dict = session.get("cart", {})
    
    cart_items = []
    total_price = 0
    
    if cart_dict:
        product_ids = [int(pid) for pid in cart_dict.keys()]
        products = Product.query.filter(Product.id.in_(product_ids)).all()
        
        for p in products:
            qty = cart_dict[str(p.id)]
            item_total = p.price * qty
            total_price += item_total
            cart_items.append({
                "product": p,
                "quantity": qty,
                "total": item_total
            })

    return render_template_string("""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Корзина — Чекушников</title>
            <link rel="stylesheet" href="/static/style.css">
        </head>
        <body>
            <div class="hero" style="align-items: flex-start; padding-top: 40px;">
                <div class="hero-card" style="max-width: 900px; text-align: left;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
                        <a href="/catalog" class="back-link" style="margin: 0;">← В каталог</a>
                        <a href="/logout" class="back-link" style="margin: 0; color: #888;">Выйти</a>
                    </div>

                    <h1 class="hero-title">Корзина</h1>

                    {% with messages = get_flashed_messages(with_categories=true) %}
                        {% if messages %}
                            {% for category, message in messages %}
                                <div class="alert alert-{{ category }}">{{ message }}</div>
                            {% endfor %}
                        {% endif %}
                    {% endwith %}

                    {% if not cart_items %}
                        <p class="hero-subtitle">Ваша корзина пуста.</p>
                        <a href="/catalog" class="btn btn-primary">Перейти в каталог</a>
                    {% else %}
                        <div class="about-list">
                            {% for item in cart_items %}
                                <div class="about-item" style="display: flex; justify-content: space-between; align-items: center;">
                                    <div style="display: flex; align-items: center; gap: 15px;">
                                        <img src="{{ url_for('static', filename='images/' + item.product.image_url) }}" alt="" style="width: 60px; height: 60px; object-fit: cover; border-radius: 8px;">
                                        <div>
                                            <h3 style="margin: 0;">{{ item.product.title }}</h3>
                                            <p style="margin: 0; color: #888;">{{ item.quantity }} шт. × {{ item.product.price }} ₽</p>
                                        </div>
                                    </div>
                                    <div style="font-weight: bold; color: #d32f2f; font-size: 1.2rem;">
                                        {{ item.total }} ₽
                                    </div>
                                </div>
                            {% endfor %}
                        </div>

                        <div style="margin-top: 20px; padding-top: 20px; border-top: 2px solid #eee; display: flex; justify-content: space-between; align-items: center;">
                            <h2 style="color: #333;">Итого: <span style="color: #d32f2f;">{{ total_price }} ₽</span></h2>
                            <a href="/delivery" class="btn btn-primary">Оформить заказ</a>
                        </div>
                    {% endif %}
                </div>
            </div>
        </body>
        </html>
    """, cart_items=cart_items, total_price=total_price)


@app.route("/add-to-cart/<int:product_id>")
def add_to_cart(product_id):
    if "cart" not in session:
        session["cart"] = {}
    
    pid = str(product_id)
    current_qty = session["cart"].get(pid, 0)
    session["cart"][pid] = current_qty + 1
    session.modified = True
    
    flash("Товар добавлен в корзину!", "success")
    return redirect(url_for("catalog"))


@app.route("/delivery", methods=["GET", "POST"])
def delivery():
    if request.method == "POST":
        if not session.get("user_id"):
            flash("Войдите в аккаунт, чтобы сделать заказ.", "danger")
            return redirect(url_for("login"))
        
        new_order = Order(
            user_id=session["user_id"],
            city=request.form.get("city", "").strip(),
            street=request.form.get("street", "").strip(),
            house=request.form.get("house", "").strip(),
            apartment=request.form.get("apartment", "").strip(),
            entrance=request.form.get("entrance", "").strip(),
            comment=request.form.get("comment", "").strip()
        )
        db.session.add(new_order)
        db.session.commit()
        session.pop("cart", None)
        flash("Заказ успешно оформлен! Оплата при получении.", "success")
        return redirect(url_for("my_orders"))

    return render_template_string("""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Доставка — Чекушников</title>
            <link rel="stylesheet" href="/static/style.css">
        </head>
        <body>
            <div class="hero">
                <div class="hero-card form-card" style="max-width: 600px;">
                    <a href="/" class="back-link">← На главную</a>

                    <h1 class="hero-title">Оформление доставки</h1>
                    <p class="hero-subtitle">Укажите адрес, и мы быстро доставим ваш заказ.</p>

                    {% with messages = get_flashed_messages(with_categories=true) %}
                        {% if messages %}
                            {% for category, message in messages %}
                                <div class="alert alert-{{ category }}">{{ message }}</div>
                            {% endfor %}
                        {% endif %}
                    {% endwith %}

                    <form method="POST" action="/delivery" class="form">
                        <div class="form-group">
                            <label for="city">Город</label>
                            <input type="text" id="city" name="city" placeholder="Например, Москва" required>
                        </div>
                        <div class="form-group">
                            <label for="street">Улица</label>
                            <input type="text" id="street" name="street" placeholder="ул. Ленина" required>
                        </div>
                        <div style="display: flex; gap: 15px;">
                            <div class="form-group" style="flex: 1;">
                                <label for="house">Дом</label>
                                <input type="text" id="house" name="house" placeholder="12" required>
                            </div>
                            <div class="form-group" style="flex: 1;">
                                <label for="apartment">Квартира</label>
                                <input type="text" id="apartment" name="apartment" placeholder="45" required>
                            </div>
                        </div>
                        <div class="form-group">
                            <label for="entrance">Подъезд (необязательно)</label>
                            <input type="text" id="entrance" name="entrance" placeholder="Например, 2">
                        </div>
                        <div class="form-group">
                            <label for="comment">Комментарий к заказу</label>
                            <textarea id="comment" name="comment" placeholder="Позвоните за 10 минут до прибытия..." rows="3" style="resize: vertical; padding: 12px 14px; border: 2px solid #e0e0e0; border-radius: 10px; font-family: inherit; font-size: 1rem;"></textarea>
                        </div>
                        <button type="submit" class="btn btn-primary btn-block">Заказать</button>
                    </form>

                </div>
            </div>
        </body>
        </html>
    """)


@app.route("/my-orders")
def my_orders():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    
    orders = Order.query.filter_by(user_id=session["user_id"]).order_by(Order.created_at.desc()).all()
    
    return render_template_string("""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Мои заказы — Чекушников</title>
            <link rel="stylesheet" href="/static/style.css">
        </head>
        <body>
            <div class="hero" style="align-items: flex-start; padding-top: 40px;">
                <div class="hero-card" style="max-width: 900px; text-align: left;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
                        <a href="/catalog" class="back-link" style="margin: 0;">← В каталог</a>
                        <a href="/logout" class="back-link" style="margin: 0; color: #888;">Выйти</a>
                    </div>
                    <h1 class="hero-title">История заказов</h1>
                    
                    {% with messages = get_flashed_messages(with_categories=true) %}
                        {% if messages %}
                            {% for category, message in messages %}
                                <div class="alert alert-{{ category }}">{{ message }}</div>
                            {% endfor %}
                        {% endif %}
                    {% endwith %}

                    <div class="about-list">
                        {% for o in orders %}
                            <div class="about-item">
                                <span class="about-icon">📦</span>
                                <div>
                                    <h3>Заказ #{{ o.id }} от {{ o.created_at.strftime('%d.%m.%Y %H:%M') }}</h3>
                                    <p>Адрес: {{ o.city }}, ул. {{ o.street }}, д. {{ o.house }}, кв. {{ o.apartment }}</p>
                                    {% if o.entrance %}<p>Подъезд: {{ o.entrance }}</p>{% endif %}
                                    {% if o.comment %}<p style="color: #888;">Комментарий: {{ o.comment }}</p>{% endif %}
                                </div>
                            </div>
                        {% else %}
                            <p>Вы еще ничего не заказывали.</p>
                        {% endfor %}
                    </div>
                </div>
            </div>
        </body>
        </html>
    """, orders=orders)


@app.route("/admin/orders")
def admin_orders():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    
    user = User.query.get(session["user_id"])
    if not user.is_admin:
        flash("Доступ запрещен.", "danger")
        return redirect(url_for("index"))

    today_filter = request.args.get("today")
    
    if today_filter:
        today = date.today()
        orders = Order.query.filter(db.func.date(Order.created_at) == today).order_by(Order.created_at.desc()).all()
    else:
        orders = Order.query.order_by(Order.created_at.desc()).all()

    return render_template_string("""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Админ-панель — Чекушников</title>
            <link rel="stylesheet" href="/static/style.css">
        </head>
        <body>
            <div class="hero" style="align-items: flex-start; padding-top: 40px;">
                <div class="hero-card" style="max-width: 1000px; text-align: left;">
                    
                    <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
                        <a href="/logout" class="back-link" style="color: #888;">Выйти</a>
                        <a href="/catalog" class="back-link" style="margin: 0;">В каталог →</a>
                    </div>

                    <h1 class="hero-title">Панель Администратора</h1>
                    
                    <div style="margin: 20px 0; display: flex; gap: 10px;">
                        <a href="/admin/orders" class="btn {{ 'btn-primary' if not request.args.get('today') else 'btn-ghost' }}">Все заказы</a>
                        <a href="/admin/orders?today=1" class="btn {{ 'btn-primary' if request.args.get('today') else 'btn-ghost' }}">Заказы на сегодня</a>
                    </div>

                    <div class="about-list">
                        {% for o in orders %}
                            <div class="about-item">
                                <span class="about-icon">🛒</span>
                                <div>
                                    <h3>Заказ #{{ o.id }} | Клиент: {{ o.user.username }}</h3>
                                    <p>Дата: {{ o.created_at.strftime('%d.%m.%Y %H:%M') }}</p>
                                    <p>Адрес: {{ o.city }}, ул. {{ o.street }}, д. {{ o.house }}, кв. {{ o.apartment }} {% if o.entrance %}(подъезд {{ o.entrance }}){% endif %}</p>
                                    {% if o.comment %}<p style="color: #d32f2f;">Комментарий: {{ o.comment }}</p>{% endif %}
                                </div>
                            </div>
                        {% else %}
                            <p>Заказов пока нет.</p>
                        {% endfor %}
                    </div>
                </div>
            </div>
        </body>
        </html>
    """, orders=orders)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)