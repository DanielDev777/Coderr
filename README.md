# Coderr API

A Django REST Framework API for a freelance service marketplace platform.

## Prerequisites

- Python 3.8+
- pip

## Setup

1. Clone the repository and navigate to the backend directory:
```bash
cd backend
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
# Copy the template file
cp .env.template .env  # Linux/Mac
copy .env.template .env  # Windows
```

Generate a Django secret key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Open `.env` and replace `your-secret-key-here` with the generated key:
```
SECRET_KEY='your-generated-secret-key-here'
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create a superuser (optional, for admin access):
```bash
python manage.py createsuperuser
```

7. Start the development server:
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`

## Authentication

Most endpoints require authentication using Token Authentication.

After registration or login, include the token in request headers:
```
Authorization: Token <your-token-here>
```

## API Endpoints

### Users

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/register/` | Register new user (business or customer) | No |
| POST | `/api/login/` | Login and get authentication token | No |
| GET | `/api/profiles/<user_id>/` | Get user profile details | Yes |
| PATCH | `/api/profiles/<user_id>/` | Update user profile | Yes (owner) |
| GET | `/api/business-profiles/` | List all business profiles | Yes |
| GET | `/api/customer-profiles/` | List all customer profiles | Yes |

### Offers

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/offers/` | List all offers (with filters) | No |
| POST | `/api/offers/` | Create new offer | Yes (business) |
| GET | `/api/offers/<id>/` | Get offer details | Yes |
| PATCH | `/api/offers/<id>/` | Update offer | Yes (owner) |
| DELETE | `/api/offers/<id>/` | Delete offer | Yes (owner) |
| GET | `/api/offerdetails/<id>/` | Get specific offer tier details | Yes |

**Query Parameters for GET /api/offers/:**
- `creator_id` - Filter by business user ID
- `min_price` - Filter by minimum price
- `max_delivery_time` - Filter by maximum delivery time
- `search` - Search in title and description
- `ordering` - Sort by `updated_at` or `min_price`

### Orders

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/orders/` | List user's orders | Yes |
| POST | `/api/orders/` | Create order from offer detail | Yes (customer) |
| GET | `/api/orders/<id>/` | Get order details | Yes |
| PATCH | `/api/orders/<id>/` | Update order status | Yes (business) |
| DELETE | `/api/orders/<id>/` | Delete order | Yes (admin) |
| GET | `/api/order-count/<business_user_id>/` | Count in-progress orders | Yes |
| GET | `/api/completed-order-count/<business_user_id>/` | Count completed orders | Yes |

### Reviews

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/reviews/` | List all reviews (with filters) | Yes |
| POST | `/api/reviews/` | Create review for business user | Yes (customer) |
| PATCH | `/api/reviews/<id>/` | Update review | Yes (owner) |
| DELETE | `/api/reviews/<id>/` | Delete review | Yes (owner) |

**Query Parameters for GET /api/reviews/:**
- `business_user_id` - Filter by business user
- `reviewer_id` - Filter by reviewer
- `ordering` - Sort by `updated_at` or `rating`

### Platform Statistics

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/base-info/` | Get platform statistics | No |

Returns: review count, average rating, business profile count, and offer count.

## Running Tests

Run all tests:
```bash
python manage.py test
```

Run tests for specific app:
```bash
python manage.py test users
python manage.py test offers
python manage.py test orders
python manage.py test reviews
```

Run with verbose output:
```bash
python manage.py test -v 2
```

## Project Structure

```
backend/
├── core/           # Project settings and configuration
├── users/          # User authentication and profiles
├── offers/         # Service offers management
├── orders/         # Order processing
├── reviews/        # Review system
└── media/          # Uploaded files (images)
```

## Development Notes

- SQLite database is used by default (db.sqlite3)
- Media files are stored in `media/` directory
- Profile pictures: `media/profile_pictures/`
- Offer images: `media/offer_images/`
