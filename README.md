# Django Service Marketplace Backend

![Django](https://img.shields.io/badge/Django-5.2.3-092E20?style=flat-square&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-3.16.0-ff1709?style=flat-square&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python&logoColor=white)

A Django REST Framework backend for a service marketplace where businesses can offer services and customers can place orders.

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/PhilippSchoenborn/Coderr_backend.git
cd Coderr_backend
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # macOS/Linux
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Setup

```bash
python manage.py migrate
```

### 5. Create Superuser

```bash
python manage.py createsuperuser
```

### 6. Load Test Data (Optional)

```bash
python manage.py loaddata fixtures/test_data.json
```

### 7. Run Development Server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/api/`

## 📊 Core Features

- **User Management**: Business and Customer profiles with authentication
- **Service Marketplace**: Businesses create offers with multiple pricing tiers
- **Order System**: Customers can order services and track progress
- **Review System**: Customers can review completed services
- **Advanced Filtering**: Search and filter offers by price, delivery time, etc.
- **Permission System**: Role-based access control (Business vs Customer)

## 🔐 Authentication

### Login
```bash
POST /api/login/
{
  "username": "your_username",
  "password": "your_password"
}
```

### Register
```bash
POST /api/registration/
{
  "username": "new_user",
  "email": "user@example.com",
  "password": "password123",
  "profile_type": "customer"  # or "business"
}
```

## 📱 Main API Endpoints

| Endpoint | Method | Description | Permission |
|----------|--------|-------------|------------|
| `/api/public-offers/` | GET | List all offers | Public |
| `/api/offers/` | GET, POST | Manage offers | Business Only |
| `/api/offers/{id}/` | GET, PUT, DELETE | Single offer | Owner/Public Read |
| `/api/orders/` | GET, POST | Manage orders | Authenticated |
| `/api/reviews/` | GET, POST | Manage reviews | Customer Only |
| `/api/profiles/` | GET | List profiles | Authenticated |
| `/api/me/` | GET, PUT | Current user profile | Owner |

## 🔍 Filtering & Search

### Offers Filtering
```bash
# Filter by price range
GET /api/public-offers/?min_price=50&max_price=500

# Filter by delivery time
GET /api/public-offers/?max_delivery_time=7

# Search in title/description
GET /api/public-offers/?search=web design

# Pagination
GET /api/public-offers/?page=1&page_size=10
```

## 🏗️ Project Structure

```
marketplace_project_restored/
├── core/                 # Main project settings
├── apps/
│   ├── authentication/  # User auth & registration
│   ├── profiles/        # User profiles
│   ├── offers/         # Service offers
│   ├── orders/         # Order management
│   └── reviews/        # Review system
├── media/              # File uploads
├── tests/              # Test files
└── requirements.txt    # Python dependencies
```

## 🧪 Testing

### Run All Tests
```bash
python manage.py test
```

### Run Specific App Tests
```bash
python manage.py test apps.offers
python manage.py test apps.orders
```

### Test API Endpoints
Use the provided REST Client files in `/tests/` folder:
- `tests/ENDPOINT_Filter_Tests.md`
- `tests/FILTER_SIMPLE.http`

## 🛠️ Development

### Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Create New App
```bash
python manage.py startapp new_app_name
```

### Admin Interface
Access Django admin at `http://127.0.0.1:8000/admin/`

## 📝 Environment Variables

Create a `.env` file in the project root:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
```

## 📚 Additional Documentation

- **API Documentation**: See `/tests/` folder for detailed endpoint testing examples
- **Security**: Role-based permissions ensure proper access control
- **Database**: SQLite for development, easily configurable for production
- **File Uploads**: Media files stored in `/media/` directory

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.
