# Contacts API

A REST API for managing contacts with authentication, email verification, rate limiting, and avatar upload.

Built with FastAPI, PostgreSQL, SQLAlchemy, Alembic, JWT, Redis, Cloudinary, Docker, and Poetry.

---

## Features

- user registration and login
- password hashing
- JWT authentication
- email verification
- resend verification email
- get current user profile
- upload user avatar with Cloudinary
- rate limiting for `/api/users/me`
- CORS support
- create, read, update, delete contacts
- search contacts by first name, last name, or email
- get contacts with birthdays in the next 7 days
- users can access only their own contacts

---

## Tech Stack

- Python
- FastAPI
- SQLAlchemy async
- PostgreSQL
- Alembic
- Pydantic
- JWT
- Redis
- SlowAPI
- FastAPI-Mail
- Cloudinary
- Docker
- Docker Compose
- Poetry

---

## Installation

Clone the repository:

```bash
git clone <repo-url>
cd <project-folder>
```

---

## Environment Variables

Create a `.env` file in the project root.

```env
DB_URL=postgresql+asyncpg://postgres:567234@db:5432/contacts_app

JWT_SECRET=your_secret_key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_SECONDS=3600

MAIL_USERNAME=your_email@meta.ua
MAIL_PASSWORD=your_mail_password
MAIL_FROM=your_email@meta.ua
MAIL_PORT=465
MAIL_SERVER=smtp.meta.ua
MAIL_FROM_NAME=Contacts API
MAIL_STARTTLS=False
MAIL_SSL_TLS=True
USE_CREDENTIALS=True
VALIDATE_CERTS=False

CLD_NAME=your_cloudinary_name
CLD_API_KEY=your_cloudinary_api_key
CLD_API_SECRET=your_cloudinary_api_secret

REDIS_URL=redis://redis:6379
```

---

## Run with Docker Compose

Build and start all services:

```bash
docker compose up --build
```

Run containers in background:

```bash
docker compose up -d
```

Stop containers:

```bash
docker compose down
```

---

## Application

Application URL:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

---

## API Endpoints

### Auth

- `POST /api/auth/register` - register new user
- `POST /api/auth/login` - login and get access token
- `GET /api/auth/confirmed_email/{token}` - confirm email
- `POST /api/auth/request_email` - resend confirmation email

### Users

- `GET /api/users/me` - get current user
- `PATCH /api/users/avatar` - update user avatar

### Contacts

- `GET /api/contacts/` - get all user contacts
- `GET /api/contacts/{contact_id}` - get contact by ID
- `POST /api/contacts/` - create contact
- `PUT /api/contacts/{contact_id}` - update contact
- `DELETE /api/contacts/{contact_id}` - delete contact
- `GET /api/contacts/search/?query=value` - search contacts
- `GET /api/contacts/birthdays/` - upcoming birthdays

---

## Example Contact Request

```json
{
  "first_name": "Anna",
  "last_name": "Ivanova",
  "email": "anna@example.com",
  "phone": "+31612345678",
  "birthday": "1995-05-10",
  "additional_data": "Friend"
}
```

---

## Authentication

Protected routes require a Bearer token.

Example header:

```text
Authorization: Bearer your_access_token
```

Login endpoint uses form data:

```text
username=your_username
password=your_password
```

---

## Project Structure

```text
src/
  api/
    auth.py
    contacts.py
    users.py
  conf/
    config.py
  database/
    db.py
    models.py
  repository/
    contacts.py
    users.py
  services/
    auth.py
    email.py
    limiter.py
    upload_file.py
    templates/
      verify_email.html
  schemas.py

main.py

migrations/

Dockerfile
docker-compose.yml
.dockerignore
```

---

## Notes

- all sensitive data is stored in `.env`
- `.env` should not be committed to GitHub
- use `.env.example` for example configuration
- passwords are stored only as hashes
- users can access only their own contacts
- Redis is used for rate limiting