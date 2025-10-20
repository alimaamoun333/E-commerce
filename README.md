# 🛍️ E-commerce Product API

## 📘 Project Overview
The **E-commerce Product API** is a backend service built with **Django REST Framework (DRF)** that provides endpoints to manage products and users for an online store.  
It allows authenticated users to perform **CRUD operations** (Create, Read, Update, Delete) on products, while also supporting user management and authentication.  

This project is part of a learning milestone aimed at building scalable RESTful APIs using Django, integrating environment management, CORS headers, and API documentation tools like Swagger.

---

## 🚀 Features

### 🧩 Core Features
- **User Management**
  - Create, view, update, and delete user accounts.
  - Secure password storage with Django’s authentication system.

- **Product Management**
  - Add new products with details (name, description, price, quantity, etc.).
  - Retrieve all products or a single product by ID.
  - Update and delete existing products.

- **Authentication & Permissions**
  - Token-based authentication for secure access.
  - Only authorized users can modify or delete products.

- **API Documentation**
  - Interactive documentation available via **Swagger UI** and **ReDoc**.

- **Environment Configuration**
  - Secure management of sensitive data using `django-environ`.

- **CORS Support**
  - Cross-Origin Resource Sharing enabled via `django-cors-headers` for frontend integration.

---

## 📄 API Documentation

### Base URL
```
https://your-api-name.onrender.com/api/v1/
```

### 🔐 Authentication
Use **Token Authentication** (JWT or DRF Token depending on setup).  
Include your token in the header:
```
Authorization: Token <your_token>
```

---

### 📦 Product Endpoints

| Method | Endpoint | Description |
|--------|-----------|-------------|
| `GET` | `/products/` | Retrieve a list of all products |
| `GET` | `/products/<id>/` | Retrieve details of a specific product |
| `POST` | `/products/` | Create a new product |
| `PUT` | `/products/<id>/` | Update an existing product |
| `DELETE` | `/products/<id>/` | Delete a product |

#### Example: Create a Product
**POST** `/products/`
```json
{
  "name": "Wireless Mouse",
  "description": "Ergonomic wireless mouse with USB receiver",
  "price": 25.99,
  "quantity": 100
}
```

#### Example: Response
```json
{
  "id": 1,
  "name": "Wireless Mouse",
  "description": "Ergonomic wireless mouse with USB receiver",
  "price": 25.99,
  "quantity": 100,
  "created_at": "2025-10-20T08:45:00Z"
}
```

---

### 👤 User Endpoints

| Method | Endpoint | Description |
|--------|-----------|-------------|
| `POST` | `/users/register/` | Register a new user |
| `POST` | `/users/login/` | Authenticate and obtain a token |
| `GET` | `/users/profile/` | Retrieve user profile (authenticated) |

#### Example: Register User
**POST** `/users/register/`
```json
{
  "username": "ali123",
  "email": "ali@example.com",
  "password": "strongpassword123"
}
```

---

### 🧭 API Documentation URLs

Once the server is running, access:
- **Swagger UI:** `/swagger/`
- **ReDoc:** `/redoc/`

---

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/ecommerce-api.git
cd ecommerce-api
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate   # on macOS/Linux
venv\Scripts\activate      # on Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables
Create a `.env` file in your root directory:
```
DEBUG=True
SECRET_KEY=your_secret_key_here
DATABASE_URL=mysql://username:password@localhost:3306/ecommerce_db
ALLOWED_HOSTS=127.0.0.1,localhost
```

### 5. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Run the Server
```bash
python manage.py runserver
```

Your API will be available at:  
👉 `http://127.0.0.1:8000/api/v1/`

---

## 📁 Folder Structure
```
ecommerce-api/
├── manage.py
├── requirements.txt
├── .env
├── ecommerce/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── products/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── urls.py
│   └── tests.py
└── users/
    ├── models.py
    ├── views.py
    ├── serializers.py
    ├── urls.py
    └── tests.py
```

---

## 🧑‍💻 Author
**Ali Maamoun**  

_“Learning and building one project at a time!”_

---

## 🪪 License
This project is licensed under the **MIT License** – feel free to use and modify it.

