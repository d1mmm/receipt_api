# Receipt API

**Tech stack:** Python 3.8, FastAPI, SQLAlchemy, PostgresSQL, JWT, Pydantic

A simple async REST-service for user registration/login and creating/viewing sales receipts, with support for:

- JWT-based auth (stored in HttpOnly cookie)  
- Decimal-accurate money fields  
- Filtering and pagination of your own receipts  
- Public text-view of any receipt by ID  
- Automated tests with pytest + in-memory SQLite  

---

## Prerequisites

- Python 3.8 or newer  
- PostgresSQL (or SQLite for quick tests)
---

## Installation

1. **Clone the repo**  
   ```bash
   git clone git@github.com:d1mmm/receipt_api.git
   cd receipt_api
   
2. **Create & activate a virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   
3. **Install build tools (optional)**
   ```bash
   pip install --upgrade pip setuptools wheel

4. **Install from PyPI-style package**
   *This will install the package and register the CLI entry point receipt-api:*
   ```bash
   python setup.py sdist bdist_wheel
   pip install .

5. **Configure environment**
   *Create a file named .env in the project root with*
   ```bash
   DATABASE_URL=postgresql+asyncpg://db_user:db_pass@localhost:5432/your_db
   JWT_SECRET=your_super_secret_key

## Running the service
   *Once installed via setup.py, you can start the API with the included CLI*
   ```bash
     receipt-api
   ```

## API Endpoints

1. **Register**
   ```bash
   curl -X POST http://localhost:8000/register -H "Content-Type: application/json" -d '{
    "username": "newuser",
    "full_name": "New User",
    "password": "newpass"}'
2. **Login**
   ```bash
   curl -X POST http://localhost:8000/login -H "Content-Type: application/json" -d '{"username":"newuser","password":"newpass"}' -c cookies.txt
3. **Create a receipt**
   ```bash
   curl -X POST http://localhost:8000/receipts -H "Content-Type: application/json" -b cookies.txt -d '{
    "products": [
      {"name":"ItemA","price":10.0,"quantity":2},
      {"name":"ItemB","price":5.5,"quantity":3}
    ],
    "payment": {"type":"cash","amount":40.0}}'
4. **List your receipts**
   ```bash
   curl -X GET http://localhost:8000/receipts -b cookies.txt
   curl -G http://localhost:8000/receipts -b cookies.txt --data-urlencode "skip=10" --data-urlencode "limit=5"
   curl -G http://localhost:8000/receipts -b cookies.txt --data-urlencode "date_from=2025-04-01T00:00:00" --data-urlencode "date_to=2025-04-30T23:59:59" --data-urlencode "min_total=100.0" --data-urlencode "payment_type=cashless"
5. **Get one receipt**
   ```bash
   curl -X GET http://localhost:8000/receipts/1 -b cookies.txt
6. **Public text-view of receipt**
   ```bash
   curl -X GET "http://localhost:8000/public/receipts/1?width=50"
   
## Testing

1. **Install dev dependencies:**
   ```bash
   pip install -r requirements.dev.txt

2. **Run tests:**
   ```bash
   pytest tests/
   
# Contributing
**Feel free to submit issues and pull requests to contribute to the project.**

# License
**This project is licensed under the MIT License.**


