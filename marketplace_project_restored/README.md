# 🏪 Django Service Marketplace Backend

![Django](https://img.shields.io/badge/Django-5.2.3+-092E20?style=for-the-badge&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-3.16.0+-ff1709?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

A comprehensive, production-ready Django REST Framework backend for a service marketplace platform. This application enables businesses to offer services, customers to place orders, and facilitates a complete review system with user authentication and profile management.

## 📋 Table of Contents

- [🚀 Overview](#-overview)
- [✨ Key Features](#-key-features)
- [🏗️ Architecture & Design](#️-architecture--design)
- [📦 Project Structure](#-project-structure)
- [🛠️ Installation & Setup](#️-installation--setup)
- [📚 API Documentation](#-api-documentation)
- [🔐 Authentication & Permissions](#-authentication--permissions)
- [💾 Database Schema](#-database-schema)
- [🧪 Testing](#-testing)
- [📁 File Upload & Media Handling](#-file-upload--media-handling)
- [🚀 Deployment](#-deployment)

## 🚀 Overview

This Django REST Framework application serves as the backend for a comprehensive service marketplace where:

- **Business Users** can create profiles, list their services (offers), manage orders, and receive reviews
- **Customer Users** can browse services, place orders, and leave reviews for businesses
- **System Administrators** can oversee the entire platform through Django's admin interface

The platform supports various service types with detailed descriptions, pricing tiers, image uploads, and a robust order management system with status tracking.

## ✨ Key Features

### 🔑 Authentication & User Management
- **Token-based authentication** using Django REST Framework's built-in TokenAuthentication
- **User registration and login** with email and username support
- **Profile management** with separate business and customer profiles
- **Secure password handling** with Django's built-in password validation

### 👤 Profile System
- **Business Profiles**: Company information, contact details, profile images
- **Customer Profiles**: Personal information, order history, review management
- **Profile image uploads** with automatic file handling and validation

### 🛍️ Service Marketplace
- **Offer Management**: Create, update, and delete service offerings
- **Rich Service Descriptions**: Detailed descriptions, features, pricing tiers
- **Image Support**: Multiple images per offer with automatic resizing
- **Categorization**: Flexible service categorization system

### 📦 Order Management
- **Complete Order Lifecycle**: From creation to completion
- **Status Tracking**: Pending, In Progress, Completed, Cancelled
- **Order Details**: Comprehensive order information and history
- **Business-Customer Communication**: Order-based messaging system

### ⭐ Review System
- **Rating System**: 1-5 star ratings for completed orders
- **Review Management**: Create, update, and moderate reviews
- **Business Analytics**: Average ratings and review statistics
- **Review Authenticity**: Only customers who completed orders can review

### 🛡️ Security & Permissions
- **Role-based Access Control**: Business vs Customer permissions
- **Owner-based Permissions**: Users can only modify their own content
- **Django's Security Features**: CSRF protection, SQL injection prevention
- **Input Validation**: Comprehensive form and API validation

## 🏗️ Architecture & Design

This project follows Django best practices and implements a clean, modular architecture:

### 📁 App Structure
```
marketplace_project/
├── core/                        # Project configuration
│   ├── settings.py             # Django settings
│   ├── urls.py                 # Main URL configuration
│   ├── wsgi.py                 # WSGI configuration
│   └── asgi.py                 # ASGI configuration
├── auth_app/                    # Authentication & user management
│   ├── api/
│   │   ├── views.py            # Authentication views
│   │   ├── serializers.py      # User serializers
│   │   └── urls.py             # Auth API URLs
│   ├── models.py               # User model extensions
│   ├── admin.py                # User admin interface
│   └── apps.py                 # App configuration
├── profiles_app/                # User profiles
│   ├── api/
│   │   ├── views.py            # Profile CRUD operations
│   │   ├── serializers.py      # Profile serializers
│   │   └── urls.py             # Profile API URLs
│   ├── models.py               # Profile models
│   ├── admin.py                # Profile admin
│   └── apps.py                 # App configuration
├── offers_app/                  # Service offerings
│   ├── api/
│   │   ├── views.py            # Offer management views
│   │   ├── serializers.py      # Offer serializers
│   │   ├── permissions.py      # Offer-specific permissions
│   │   └── urls.py             # Offer API URLs
│   ├── models.py               # Offer and OfferDetail models
│   ├── admin.py                # Offer admin interface
│   └── apps.py                 # App configuration
├── orders_app/                  # Order processing
│   ├── api/
│   │   ├── views.py            # Order management views
│   │   ├── serializers.py      # Order serializers
│   │   ├── permissions.py      # Order permissions
│   │   └── urls.py             # Order API URLs
│   ├── models.py               # Order model
│   ├── admin.py                # Order admin
│   └── apps.py                 # App configuration
├── reviews_app/                 # Review system
│   ├── api/
│   │   ├── views.py            # Review CRUD operations
│   │   ├── serializers.py      # Review serializers
│   │   ├── permissions.py      # Review permissions
│   │   └── urls.py             # Review API URLs
│   ├── models.py               # Review model
│   ├── admin.py                # Review admin
│   └── apps.py                 # App configuration
├── media/                       # Uploaded files
│   ├── profiles/               # Profile images
│   └── offers/                 # Offer images
├── api_tests/                   # REST API tests
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
└── README.md                    # This documentation
```

### 🔄 API Design Pattern
- **RESTful API design** with proper HTTP methods (GET, POST, PUT, DELETE)
- **Consistent response format** with proper status codes
- **API versioning** through URL namespacing
- **Serializer-based validation** for all input data

## 📦 Project Structure

### Models Overview

**User Management:**
- `CustomUser` (extends Django's User)
- `Profile` (Business/Customer profiles)

**Marketplace:**
- `Offer` (Service offerings)
- `OfferDetail` (Detailed offer information)
- `Order` (Purchase orders)
- `Review` (Customer reviews)

### API Endpoints Structure

```
/api/auth/          # Authentication endpoints
/api/profiles/      # Profile management
/api/offers/        # Offer management
/api/orders/        # Order processing
/api/reviews/       # Review system
/api/dashboard/     # Analytics dashboard
```

## 🛠️ Installation & Setup

### Prerequisites

- **Python 3.10+**
- **pip** (Python package manager)
- **Virtual environment** (recommended)

### Local Development Setup

1. **Clone and navigate to the project:**
   ```bash
   cd marketplace_project/
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser (optional):**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

7. **Access the application:**
   - API: http://127.0.0.1:8000/api/
   - Admin: http://127.0.0.1:8000/admin/

### Alternative: Quick Setup

```bash
cd marketplace_project/
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## 📚 API Documentation

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register/` | User registration | No |
| POST | `/api/auth/login/` | User login | No |
| POST | `/api/auth/logout/` | User logout | Yes |

### Profile Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/profiles/` | Get current user profile | Yes |
| PUT | `/api/profiles/` | Update profile | Yes |
| PATCH | `/api/profiles/` | Partial profile update | Yes |

### Offer Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/offers/` | List all offers | No |
| POST | `/api/offers/` | Create new offer | Yes (Business) |
| GET | `/api/offers/{id}/` | Get offer details | No |
| PUT | `/api/offers/{id}/` | Update offer | Yes (Owner) |
| DELETE | `/api/offers/{id}/` | Delete offer | Yes (Owner) |

### Order Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/orders/` | List user orders | Yes |
| POST | `/api/orders/` | Create new order | Yes (Customer) |
| GET | `/api/orders/{id}/` | Get order details | Yes (Owner) |
| PATCH | `/api/orders/{id}/` | Update order status | Yes (Business) |

### Review System

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/reviews/` | List reviews | No |
| POST | `/api/reviews/` | Create review | Yes (Customer) |
| GET | `/api/reviews/{id}/` | Get review details | No |
| PUT | `/api/reviews/{id}/` | Update review | Yes (Owner) |
| DELETE | `/api/reviews/{id}/` | Delete review | Yes (Owner) |

### Core/Utility Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/dashboard/` | Business dashboard data | Yes (Business) |
| GET | `/api/` | API root / health check | No |

## 🔐 Authentication & Permissions

### Authentication System
- **Token Authentication**: Uses Django REST Framework's TokenAuthentication
- **Session Authentication**: Supports Django's session-based auth for admin
- **Token Management**: Automatic token creation on user registration

### Permission Classes
- **IsOwnerOrReadOnly**: Users can only modify their own content
- **IsBusinessUser**: Only business users can create offers
- **IsCustomerUser**: Only customers can place orders
- **IsAuthenticatedOrReadOnly**: Read access for all, write for authenticated users

### User Types
- **Business Users**: Can create offers, manage orders, receive reviews
- **Customer Users**: Can place orders, write reviews, browse offers
- **Administrators**: Full access via Django admin interface

## 💾 Database Schema

### Core Models

**User Profile:**
```python
class Profile(models.Model):
    user = OneToOneField(User)
    user_type = CharField(choices=USER_TYPE_CHOICES)
    file = ImageField(upload_to='profiles/')
    location = CharField()
    tel = CharField()
    description = TextField()
```

**Service Offer:**
```python
class Offer(models.Model):
    user = ForeignKey(User)
    title = CharField()
    file = ImageField(upload_to='offers/')
    description = TextField()
    price = DecimalField()
    min_delivery_time = IntegerField()
    max_delivery_time = IntegerField()
```

**Order:**
```python
class Order(models.Model):
    customer = ForeignKey(User)
    offer_detail = ForeignKey(OfferDetail)
    status = CharField(choices=ORDER_STATUS_CHOICES)
    created_at = DateTimeField()
    updated_at = DateTimeField()
```

**Review:**
```python
class Review(models.Model):
    order = OneToOneField(Order)
    reviewer = ForeignKey(User)
    business = ForeignKey(User)
    rating = IntegerField(validators=[1, 5])
    description = TextField()
```

## 🧪 Testing

The application includes a comprehensive test suite with **97 tests covering all endpoints and edge cases**.

### ✅ Test Status: ALL TESTS PASSING (97/97)

### Test Coverage Overview:
- **Authentication Tests (13)**: Registration, login, token handling, validation
- **Profile Tests (13)**: CRUD operations, permissions, file uploads
- **Offer Tests (20)**: Service management, business permissions, public access
- **Order Tests (20)**: Order lifecycle, status management, role-based access
- **Review Tests (19)**: Review system, ratings, user permissions
- **Base Info Tests (5)**: Statistics endpoints, data aggregation
- **Cross-cutting Tests (7)**: URL routing, error handling, authentication flows

### Running Tests

```bash
# Run all tests with the custom test runner
python run_tests.py

# Run specific test modules
python manage.py test tests.test_authentication
python manage.py test tests.test_profiles
python manage.py test tests.test_offers
python manage.py test tests.test_orders
python manage.py test tests.test_reviews
python manage.py test tests.test_base_info

# Run with verbose output
python manage.py test tests.test_authentication -v 2
```

### Test Features
- **Empty Database Testing**: All tests start with a clean database
- **Comprehensive Coverage**: Every endpoint tested for both happy and unhappy paths
- **Permission Testing**: Role-based access control verification
- **Data Validation**: Input validation and error handling tests
- **File Upload Testing**: Image upload functionality verification
- **Performance Testing**: Response time and concurrent request handling

### Test Results Summary
```
============================================================
✅ All tests passed successfully!
🧪 Total Tests: 97
✅ Passed: 97
❌ Failed: 0
⏱️ Execution Time: ~220 seconds
============================================================
```

### API Testing

Use the provided REST files in `api_tests/` directory for manual testing:

1. **Authentication Tests**: `registration.rest`, `login.rest`
2. **Profile Tests**: `profile_get.rest`, `profile_patch.rest`
3. **Offer Tests**: `offers_get.rest`, `offers_post.rest`, `offerdetails_get.rest`
4. **Order Tests**: `orders_get.rest`, `orders_post.rest`
5. **Dashboard Tests**: `dashboard_get.rest`

## 📁 File Upload & Media Handling

### Supported File Types
- **Profile Images**: JPG, PNG, BMP (max 5MB)
- **Offer Images**: JPG, PNG, BMP (max 10MB)

### File Storage
- **Development**: Local file system in `media/` directory
- **Production**: Configurable (AWS S3, Google Cloud Storage, etc.)

### Security
- **File validation**: Type and size checking
- **Secure upload paths**: Organized by app and date
- **Image optimization**: Automatic resizing and compression

## 🚀 Deployment

### Environment Variables

Create a `.env` file in the project root:

```env
DEBUG=False
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Configure proper `SECRET_KEY`
- [ ] Set up production database (PostgreSQL recommended)
- [ ] Configure static file serving (WhiteNoise/CDN)
- [ ] Set up media file storage (AWS S3/Google Cloud)
- [ ] Configure CORS settings
- [ ] Set up SSL/HTTPS
- [ ] Configure logging
- [ ] Set up monitoring and error tracking
- [ ] Run security audit: `python manage.py check --deploy`

### Docker Deployment (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput
RUN python manage.py migrate

EXPOSE 8000
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]
```

---

## 📁 Project Documentation

For comprehensive project information, please refer to the documentation in the `ABGABE_DOKUMENTATION/` folder:

### 🎯 Main Documentation Files:
- **[PROJEKT_ABGABE_CHECKLISTE.md](ABGABE_DOKUMENTATION/PROJEKT_ABGABE_CHECKLISTE.md)** - Complete project submission checklist and validation
- **[FRONTEND_BUG_DOCUMENTATION.md](ABGABE_DOKUMENTATION/FRONTEND_BUG_DOCUMENTATION.md)** - Documentation of known frontend issues
- **[FRONTEND_TESTING_VERFAHREN.md](ABGABE_DOKUMENTATION/FRONTEND_TESTING_VERFAHREN.md)** - Frontend testing procedures and workarounds

### 🧪 Validation Scripts:
- **`backend_validation_test.py`** - Automated backend functionality test
- **`create_frontend_test_users.py`** - Script to create test users for frontend compatibility

### ✅ Project Status:
- **Backend**: ✅ Production-ready and fully tested
- **API**: ✅ All endpoints functional and documented
- **Authentication**: ✅ Token-based auth implemented
- **Database**: ✅ Migrations complete and tested
- **Media Handling**: ✅ File uploads (Base64 + FormData) working
- **Documentation**: ✅ Comprehensive docs provided

## 🔧 Development Guidelines

### Code Style
- **PEP 8**: Follow Python style guidelines
- **Django Conventions**: Use Django naming conventions
- **Docstrings**: Document all classes and functions
- **Type Hints**: Use type hints where applicable

### Git Workflow
- **Feature Branches**: Create branches for new features
- **Descriptive Commits**: Write clear commit messages
- **Pull Requests**: Use PRs for code review
- **Testing**: Ensure all tests pass before merging

### Best Practices
- **DRY Principle**: Don't Repeat Yourself
- **SOLID Principles**: Follow object-oriented design principles
- **Security First**: Always consider security implications
- **Performance**: Profile and optimize database queries
- **Documentation**: Keep documentation up-to-date

---

## 📞 Support

For issues, questions, or contributions:

1. **Check Documentation**: Review this README and Django docs
2. **Search Issues**: Look for existing solutions
3. **Create Issue**: Provide detailed reproduction steps
4. **Contact**: Reach out to the development team

---

**Built with ❤️ using Django and Django REST Framework**
