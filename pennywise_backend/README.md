# PennyWise Backend

Django REST API backend for the PennyWise personal finance management application.

## Quick Start

### Using Docker (Recommended)

1. Copy the environment file:
```bash
cp .env.example .env
```

2. Start the services:
```bash
docker-compose up --build
```

3. Create a superuser:
```bash
docker-compose exec backend python manage.py createsuperuser
```

4. Access the API at `http://localhost:8000/api/`

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy environment file:
```bash
cp .env.example .env
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Create superuser:
```bash
python manage.py createsuperuser
```

5. Start development server:
```bash
python manage.py runserver
```

## API Endpoints

### Authentication
- `POST /api/auth/login/` - Login and get token
- `POST /api/users/register/` - Register new user

### Transactions
- `GET /api/transactions/` - List user transactions
- `POST /api/transactions/` - Create transaction
- `GET /api/transactions/summary/` - Get transaction summary
- `POST /api/transactions/bulk_create/` - Bulk create transactions

### Budgets
- `GET /api/budgets/` - List user budgets
- `POST /api/budgets/` - Create budget
- `GET /api/budgets/status/` - Get budget status

### Alert Configs
- `GET /api/alert-configs/` - List alert configurations
- `POST /api/alert-configs/` - Create alert configuration

## Testing

Run tests with:
```bash
python manage.py test
```

## Database Models

- **User**: Custom user model with Telegram integration
- **Transaction**: Financial transactions with categories
- **Budget**: Spending limits by category and period
- **AlertConfig**: Notification preferences and thresholds