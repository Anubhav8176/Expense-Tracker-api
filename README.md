# Expense Tracker API

A RESTful API for tracking personal expenses, built with **FastAPI** and **SQLAlchemy**. Supports JWT-based authentication with access and refresh token rotation, full expense CRUD, per-user data isolation, and expense filtering by date range.

Built as part of the [Expense Tracker API](https://roadmap.sh/projects/expense-tracker-api) project on [roadmap.sh](https://roadmap.sh) — the final beginner-level project in the backend roadmap track.

---

## Table of Contents

- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Authentication](#authentication)
- [API Reference](#api-reference)
  - [Auth Endpoints](#auth--auth)
  - [Expense Endpoints](#expenses--expenses)
- [Data Models](#data-models)
- [Security Notes](#security-notes)
- [Roadmap.sh Requirements](#roadmapsh-requirements)
- [License](#license)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| ORM | SQLAlchemy |
| Database | SQLite (`expense.db`) |
| Auth | JWT (Access + Refresh Tokens) |
| Password Hashing | Bcrypt |
| Validation | Pydantic v2 |
| Config | python-dotenv |

---

## Project Structure

```
Expense-Tracker-api/
├── core/
│   ├── authentication.py     # JWT creation, hashing, get_current_user
│   └── config.py             # Settings loaded from .env
├── db/
│   ├── session.py            # SQLAlchemy engine & session
│   ├── User.py               # User model
│   ├── Expense.py            # Expense model
│   └── RefreshToken.py       # RefreshToken model
├── routers/
│   ├── router.py             # Root router (mounts auth + expense)
│   ├── auth.py               # Auth endpoints
│   └── expense.py            # Expense CRUD endpoints
├── schemas/
│   └── models.py             # Pydantic request/response schemas
├── main.py                   # FastAPI app entry point
└── .env                      # Environment variables
```

---

## Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/Anubhav8176/Expense-Tracker-api.git
cd Expense-Tracker-api
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install fastapi uvicorn sqlalchemy pydantic[email] python-jose[cryptography] passlib[bcrypt] python-dotenv
```

### 4. Configure environment variables

Create a `.env` file in the root directory:

```env
APP_NAME="Expense Tracker"
ENVIRONMENT=development
DEBUG=False

DATABASE_URL=sqlite:///./expense.db

SECRET_KEY=your_secret_key_here
ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_EXPIRE_DAYS=30

ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
```

> ⚠️ Never commit your `.env` file to version control. Add it to `.gitignore`.

### 5. Run the server

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.  
Interactive Swagger docs are at `http://localhost:8000/docs`.

---

## Authentication

This API uses a **dual-token system**:

- **Access Token** — Short-lived JWT used to authorize requests. Pass it in the `Authorization` header as `Bearer <token>`.
- **Refresh Token** — Long-lived token (30 days) stored in the database. Used to issue a new access token without requiring re-login.

### Token Rotation Behaviour

| Scenario | Result |
|---|---|
| Refresh token is **valid** | Issues a new access token; refresh token is reused |
| Refresh token is **expired** | Revokes old token; issues new access + refresh token |
| Refresh token is **revoked** | Returns `401 Unauthorized` |
| Refresh token **not found** | Returns `401 Unauthorized` |

On **login**, all previously active refresh tokens for the user are revoked before issuing a new one.

---

## API Reference

### Auth — `/auth`

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/auth/register` | Register a new user | ❌ |
| `POST` | `/auth/login` | Login and receive tokens | ❌ |
| `POST` | `/auth/refresh` | Rotate access/refresh tokens | ❌ |

---

#### `POST /auth/register`

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword"
}
```

**Response `201`:**
```json
{
  "access_token": "<jwt>",
  "refresh_token": "<token>"
}
```

---

#### `POST /auth/login`

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "securepassword"
}
```

**Response `200`:**
```json
{
  "access_token": "<jwt>",
  "refresh_token": "<token>"
}
```

---

#### `POST /auth/refresh`

**Request Body:**
```json
{
  "refresh_token": "<token>"
}
```

**Response `200`:**
```json
{
  "access_token": "<new_jwt>",
  "refresh_token": "<same_or_new_token>"
}
```

---

### Expenses — `/expenses`

> All expense endpoints require a valid `Authorization: Bearer <access_token>` header.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/expenses/` | Get all expenses (paginated, filterable) |
| `GET` | `/expenses/{id}` | Get a single expense by ID |
| `POST` | `/expenses/` | Create a new expense |
| `PUT` | `/expenses/{id}` | Update an existing expense |
| `DELETE` | `/expenses/{id}` | Delete an expense |

---

#### `GET /expenses/`

Returns a paginated list of expenses for the authenticated user. Supports optional date range filters.

**Query Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `page` | `int` | Page number (default: `1`) |
| `limit` | `int` | Results per page (default: `10`) |
| `filter` | `string` | Preset filter: `week`, `month`, `3months` |
| `start_date` | `date` | Custom range start (`YYYY-MM-DD`) |
| `end_date` | `date` | Custom range end (`YYYY-MM-DD`) |

**Examples:**

```
GET /expenses/?filter=week
GET /expenses/?filter=month
GET /expenses/?filter=3months
GET /expenses/?start_date=2026-01-01&end_date=2026-03-31
GET /expenses/?page=1&limit=10
```

**Response `200`:**
```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "title": "Groceries",
    "desc": "Weekly grocery run",
    "amount": 1500.00,
    "category": "Groceries",
    "type": "debit",
    "created_at": "2026-04-16T10:00:00Z"
  }
]
```

---

#### `GET /expenses/{id}`

Returns a single expense by ID. Returns `404` if it doesn't belong to the authenticated user.

---

#### `POST /expenses/`

**Request Body:**
```json
{
  "title": "Groceries",
  "desc": "Weekly grocery run",
  "amount": 1500.00,
  "category": "Groceries",
  "type": "debit"
}
```

**Valid categories:** `Groceries`, `Leisure`, `Electronics`, `Utilities`, `Clothing`, `Health`, `Others`

**Response `201`:** Returns the created expense object.

---

#### `PUT /expenses/{id}`

Supports **partial updates** — only include the fields you want to change.

**Request Body:**
```json
{
  "amount": 1800.00,
  "desc": "Updated grocery run"
}
```

**Response `200`:** Returns the updated expense object.

---

#### `DELETE /expenses/{id}`

**Response `204 No Content`** — No response body.

---

## Data Models

### User

| Field | Type | Description |
|---|---|---|
| `id` | UUID | Primary key |
| `name` | String | Full name |
| `email` | String | Unique email address |
| `hashed_password` | String | Bcrypt hashed password |

### Expense

| Field | Type | Description |
|---|---|---|
| `id` | UUID | Primary key |
| `user_id` | UUID | Foreign key → User |
| `title` | String | Expense title |
| `desc` | String | Description |
| `amount` | Float | Amount |
| `category` | String | One of: `Groceries`, `Leisure`, `Electronics`, `Utilities`, `Clothing`, `Health`, `Others` |
| `type` | String | `debit` or `credit` |
| `created_at` | DateTime | Auto-set on creation |

### RefreshToken

| Field | Type | Description |
|---|---|---|
| `id` | UUID | Primary key |
| `user_id` | UUID | Foreign key → User |
| `access_token` | String | Latest access token issued |
| `refresh_token` | String | Unique refresh token |
| `is_revoked` | Boolean | Whether the token has been invalidated |
| `expires_at` | DateTime | Token expiry timestamp |
| `created_at` | DateTime | Auto-set on creation |

---

## Security Notes

- Passwords are hashed with **bcrypt** before storage — plain passwords are never persisted.
- Every expense query filters by `user_id`, ensuring users can only access their own data.
- JWTs are signed with `HS256` using the `SECRET_KEY` from your `.env`.
- Refresh tokens track an `is_revoked` flag to prevent reuse of invalidated tokens.
- **Rotate your `SECRET_KEY`** in production and never expose it publicly.
---

## License

This project is open source and available under the [MIT License](LICENSE).
