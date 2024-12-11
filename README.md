# Supply Chain Management API

A modern, production-ready Supply Chain Management API built with FastAPI, SQLAlchemy, and PostgreSQL. This project demonstrates best practices in Python backend development, API design, and supply chain systems.

## Features

- Comprehensive inventory management
- Warehouse management
- Transaction tracking
- Real-time stock monitoring
- Advanced filtering and search
- Metrics and analytics
- Production-ready security
- Comprehensive documentation

## Technical Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL + SQLAlchemy
- **Cache**: Redis
- **Documentation**: OpenAPI (Swagger) + ReDoc
- **Testing**: pytest
- **Code Quality**: black, flake8, mypy
- **Monitoring**: Prometheus + Grafana
- **Deployment**: Docker + Kubernetes

## Project Structure

```
supply_chain_api/
├── src/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   ├── core/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── utils/
├── tests/
│   ├── api/
│   ├── services/
│   └── conftest.py
��── docs/
└── deployment/
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Kakachia777/supply-chain-api.git
cd supply-chain-api
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up the database:
```bash
# Create PostgreSQL database
createdb supply_chain_db

# Run migrations
alembic upgrade head
```

## Configuration

Create a `.env` file:
```env
DATABASE_URL=postgresql://user:password@localhost/supply_chain_db
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
```

## Usage

### Running the API

Development:
```bash
uvicorn src.main:app --reload
```

Production:
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### API Documentation

- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

### Example Requests

Create Inventory Item:
```bash
curl -X POST "http://localhost:8000/api/v1/inventory/items/" \
     -H "Content-Type: application/json" \
     -d '{
         "sku": "ITEM001",
         "name": "Example Item",
         "category": "raw_material",
         "unit": "piece",
         "reorder_point": 100,
         "reorder_quantity": 500
     }'
```

Create Transaction:
```bash
curl -X POST "http://localhost:8000/api/v1/inventory/transactions/" \
     -H "Content-Type: application/json" \
     -d '{
         "item_id": 1,
         "transaction_type": "receive",
         "quantity": 100,
         "reference": "PO12345"
     }'
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/api/test_inventory.py
```

### Code Quality

```bash
# Format code
black src/ tests/

# Check types
mypy src/

# Lint code
flake8 src/ tests/
```

## Deployment

### Docker

Build image:
```bash
docker build -t supply-chain-api .
```

Run container:
```bash
docker run -p 8000:8000 supply-chain-api
```

### Kubernetes

Deploy to Kubernetes:
```bash
kubectl apply -f deployment/k8s/
```

## Monitoring

The API exposes Prometheus metrics at `/metrics` including:
- Request counts and latencies
- Database operation metrics
- Business metrics (stock levels, transaction volumes)

## Security Features

- API key authentication
- Rate limiting
- Input validation
- SQL injection prevention
- CORS configuration
- Secure password hashing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For questions and support:
- GitHub Issues: [Create an issue](https://github.com/Kakachia777/supply-chain-api/issues) 