# Django REST Framework Service Marketplace Backend

This project is a robust, modularized Django REST Framework (DRF) backend for a service marketplace. It features clear domain separation, comprehensive validation, and full unhappy-path test coverage.

## 1. Features & Structure

- **Modularized Codebase:**
  - Views and serializers are split by domain (e.g., `views_profile.py`, `serializers_offer.py`).
  - All endpoints are robust, validated, and tested for both happy and unhappy paths.
  - Permissions and models are fully documented with English docstrings.
- **API Domains:**
  - **Profile:** User profile management (view, update, etc.)
  - **Offer:** Service offers, including details and filtering
  - **Order:** Placing and managing orders
  - **Review:** Customer reviews for business users
  - **Registration & Login:** User registration and authentication
  - **Misc/Public:** Miscellaneous and public endpoints
- **Testing:**
  - Unhappy-path tests for all endpoints in `api/tests_unhappy/`
  - (Optional) Happy-path tests can be expanded for full coverage
- **Validation & Error Handling:**
  - All endpoints enforce required fields, forbidden fields, and type checks
  - API responses match the documentation exactly (fields, types, pagination, filtering, etc.)
  - Comprehensive error messages and status codes for all failure scenarios
- **Documentation:**
  - Every function and class is documented with English docstrings
  - README and requirements are up to date

## 2. Setup Instructions

### a) Install Python
Ensure you have Python 3.10+ installed. Download from [python.org](https://www.python.org/downloads/).

### b) Create and Activate a Virtual Environment (Recommended)
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### c) Install Requirements
```powershell
pip install -r requirements.txt
```

### d) Database Setup
```powershell
python manage.py migrate
```

### e) (Optional) Create a Superuser
```powershell
python manage.py createsuperuser
```

### f) Start the Development Server
```powershell
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/` by default.

## 3. Project Structure

- `api/` — Main app with modularized views, serializers, models, permissions, and tests
  - `views_profile.py`, `views_offer.py`, `views_order.py`, `views_review.py`, etc.
  - `serializers_profile.py`, `serializers_offer.py`, etc.
  - `tests_unhappy/` — Unhappy-path tests for all endpoints
- `backend/` — Django project settings and URLs
- `media/` — Uploaded files (ignored by git)
- `requirements.txt` — All dependencies
- `README.md` — This documentation

## 4. Testing

To run all unhappy-path tests:
```powershell
python manage.py test api.tests_unhappy
```

You can add more tests in the `api/tests_unhappy/` or create happy-path tests as needed.

## 5. Code Quality & Best Practices

- All code is PEP8-compliant and follows Django/DRF best practices
- Each function and class is documented with English docstrings
- Dead code is removed and imports are sorted
- API responses are robust and match the documentation

## 6. Additional Notes

- Do not commit the `db.sqlite3` file or any files listed in `.gitignore` to version control.
- All DRF configuration is in `backend/settings.py`.
- For more information, see the official Django documentation: https://docs.djangoproject.com/
