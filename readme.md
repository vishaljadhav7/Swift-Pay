# SwiftPay

A SwiftPay-inspired payment backend built with a microservices architecture. Handles user auth, wallet operations, money transfers, and event-driven rewards/notifications.

---

## Architecture

Six independent services communicate over HTTP and Kafka, each with its own PostgreSQL database.

```
Client
  │
  ▼
API Gateway (Port 8000)
- JWT Authentication
- Rate Limiting
- Routing
  │
  ├──► User Service (8001) ──────── PostgreSQL
  ├──► Wallet Service (8088) ────── PostgreSQL
  ├──► Transaction Service (8002) ── PostgreSQL
  │        │
  │        │ (hyx circuit breaker on all wallet calls)
  │        │
  │        ▼
  │   Wallet Service (hold/capture/release)
  │
  │ Publish Kafka event (txn-initiated)
  │        │
  │        ├──► Notification Service (8003) ── PostgreSQL
  │        └──► Reward Service (8004) ──────── PostgreSQL
```

---

## Features

- **Auth** — JWT-based signup/login with bcrypt password hashing
- **Wallets** — Per-user wallets with separate `balance` and `available_balance` tracking
- **Money Transfers** — Hold → Capture → Credit flow with automatic rollback on failure
- **Notifications** — Receivers get notified on incoming transfers via Kafka
- **Rewards** — Senders earn points (`amount × 100`) per successful transaction via Kafka
- **Rate Limiting** — Token bucket algorithm at the gateway level (10 req/min, burst 20)
- **Circuit Breaker** — Wallet service calls are wrapped with a consecutive failure breaker (threshold: 5, recovery: 30s)
- **Idempotency** — Transactions are deduplicated via `idempotency_key`

---

## Tech Stack

| | |
|---|---|
| **FastAPI** | Async web framework for all six services |
| **PostgreSQL** | Separate database per service (true data isolation) |
| **Apache Kafka** | Event streaming for async notification and reward processing |
| **SQLAlchemy (async)** | ORM with `asyncpg` driver; pessimistic locking on wallet rows |
| **Docker Compose** | Orchestrates all services, databases, Kafka, and Zookeeper |
| **PyJWT + passlib** | Token generation and bcrypt password hashing |
| **httpx** | Async HTTP client for inter-service calls |
| **hyx** | Circuit breaker for resilient service-to-service communication |
| **uv** | Fast Python package manager and virtual environment tooling |

---

## Getting Started

**Prerequisites:** Docker and Docker Compose installed.

```bash
git clone https://github.com/your-username/razorswiftpay.git
cd razorswiftpay
```

Create `.env` files for each service. Minimum required variables:

```
# api-gateway/.env
SECRET_KEY=your_secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# user-service/.env
DATABASE_URL=postgresql+asyncpg://myuser:user123@postgres-user/user-db
SECRET_KEY=your_secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# wallet-service/.env
DATABASE_URL=postgresql+asyncpg://myuser:wallet123@postgres-wallet/wallet-db

# transaction-service/.env
DATABASE_URL=postgresql+asyncpg://txn:txn123@postgres-txn/txn-db

# notification-service/.env
DATABASE_URL=postgresql+asyncpg://myuser:notify123@postgres-notify/notify-db

# reward-service/.env
DATABASE_URL=postgresql+asyncpg://myuser:reward123@postgres-reward/reward-db
```

```bash
docker compose up --build
```

Gateway is available at `http://localhost:8000`.

---

## API Endpoints

All requests go through the gateway at port `8000`. Routes prefixed with 🔒 require a `Bearer` token.

### Auth

`POST /auth/signup` — Register a new user
```json
{ "name": "string", "email": "user@example.com", "password": "string", "admin_key": "optional" }
```

`POST /auth/login` — Returns JWT access token
```json
{ "email": "user@example.com", "password": "string" }
```

### Users
```
GET    /api/users/{user_id}    Get user profile
```

### Wallets

> Wallet service routes are prefixed `/api/v1/wallets`

```
GET    /api/v1/wallets/{user_id}         Get wallet balance
```

`POST /api/v1/wallets` — Create wallet
```json
{ "user_id": "string", "currency": "INR" }
```

`POST /api/v1/wallets/credit` — Credit funds
```json
{ "user_id": "string", "currency": "INR", "amount": 1000 }
```

`POST /api/v1/wallets/debit` — Debit funds
```json
{ "user_id": "string", "currency": "INR", "amount": 1000 }
```

`POST /api/v1/wallets/hold` — Place a hold on funds
```json
{ "user_id": "string", "currency": "INR", "amount": 1000 }
```

`POST /api/v1/wallets/capture` — Capture a hold (finalise debit)
```json
{ "hold_reference": "HOLD-..." }
```

```
POST   /api/v1/wallets/release/{hold_reference}    Release a hold (no body)
```

### Transactions 🔒

`POST /api/transactions/create` — Initiate a money transfer
```json
{ "sender_id": "string", "receiver_id": "string", "amount": 100.0, "idempotency_key": "unique-string" }
```

```
GET    /api/transactions/{transaction_id}      Get transaction by ID
GET    /api/transactions/user/{user_id}        Get all transactions for a user
```

### Rewards 🔒
```
GET    /api/rewards                    All rewards (admin)
GET    /api/rewards/user/{user_id}     Rewards for a specific user
```

### Notifications 🔒

`POST /api/notify` — Send a manual notification
```json
{ "user_id": "string", "message": "string" }
```

```
GET    /api/notify/{user_id}    Get notifications for a user
```

---

## How a Transfer Works

```
1. POST /api/transactions/create
2. Transaction saved as PENDING
3. Hold placed on sender's wallet  →  available_balance reduced
4. Receiver wallet existence verified
5. Hold captured  →  sender balance reduced
6. Receiver wallet credited
7. Transaction marked SUCCESS
8. Kafka event published  →  notification + reward created async

On any failure: hold released, sender refunded, transaction marked FAILED
```

---

## Notes

- New wallets are seeded with ₹500 (500 paise) for testing
- Holds expire after 10 minutes; a background scheduler releases them automatically
- Reward points formula: `transaction_amount × 100`
- Each service runs independently — a service restart does not affect others