# E-commerce Microservices System

A minimal multi-service e-commerce system using Docker, where each service is independently deployable and scalable.

## Services

1. **Product Service** (Port 8001)

   - FastAPI service for product management
   - Endpoints: `/products`, `/products/{id}`

2. **Cart Service** (Port 8002)

   - FastAPI service for shopping cart operations
   - Endpoints: `/cart`, `/cart/items`

3. **Order Service** (Port 8003)

   - FastAPI service for order management
   - Endpoints: `/orders`, `/orders/{id}`

4. **User Service** (Port 8004)

   - Laravel service with Sanctum authentication
   - Endpoints: `/api/auth/*`, `/api/user/*`

5. **Payment Service** (Port 8005)

   - FastAPI service for payment operations
   - Endpoints: `/balance`, `/add_balance`

6. **Inventory Service** (Port 8006)

   - FastAPI service for stock management
   - Endpoints: `/inventory`, `/inventory/{id}`

7. **Analytics Service** (Port 8007)
   - FastAPI service for sales analytics
   - Endpoints: `/analytics/sales`, `/analytics/stats`

## Prerequisites

- Docker and Docker Compose
- Git

## Setup Instructions

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd ecommerce-microservices
   ```

2. Start all services:

   ```bash
   docker-compose up --build
   ```

3. Access services:
   - Product Service: http://localhost:8001
   - Cart Service: http://localhost:8002
   - Order Service: http://localhost:8003
   - User Service: http://localhost:8004
   - Payment Service: http://localhost:8005
   - Inventory Service: http://localhost:8006
   - Analytics Service: http://localhost:8007

## Testing the Services

### User Service (Laravel)

```bash
# Register a new user
curl -X POST http://localhost:8004/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "email": "test@example.com", "password": "password123"}'

# Login
curl -X POST http://localhost:8004/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

### Product Service (FastAPI)

```bash
# List products
curl http://localhost:8001/products

# Add a product
curl -X POST http://localhost:8001/products \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Product", "price": 99.99, "description": "Test Description"}'
```

### Cart Service (FastAPI)

```bash
# Add item to cart
curl -X POST http://localhost:8002/cart/items \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "quantity": 2}'

# View cart
curl http://localhost:8002/cart
```

## Development

Each service is in its own directory with its own Dockerfile and configuration. To work on a specific service:

1. Navigate to the service directory
2. Make your changes
3. Rebuild the service:
   ```bash
   docker-compose up --build <service-name>
   ```

## Notes

- All FastAPI services use SQLite for simplicity
- User Service uses MySQL for better Laravel compatibility
- Services communicate via internal Docker network
- Each service can be scaled independently
p l a c e h o l d e r 
 
 g i t 
 
 a d d 
 
 . 
 
 p l a c e h o l d e r 
 
 
