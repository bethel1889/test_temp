# Qari FastAPI Backend

![Python](https://img.shields.io/badge/Python-3.11-3776AB.svg?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?style=for-the-badge&logo=fastapi)
![LiveKit](https://img.shields.io/badge/LiveKit-SDK-orange?style=for-the-badge&logo=livekit)
![Docker](https://img.shields.io/badge/Docker-20.10-2496ED.svg?style=for-the-badge&logo=docker)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791.svg?style=for-the-badge&logo=postgresql)

This repository contains the production-ready backend for the Qari Web3 video conferencing application. It is built with FastAPI and leverages the LiveKit Python SDK to manage real-time video rooms, handle user authentication, and process server-side events.

## Core Architecture

This project is built using a modern, scalable **Feature-Driven Architecture**, which combines principles from Vertical Slice Architecture and Clean Architecture.

*   **Vertical Slicing**: Code is organized by feature (e.g., `rooms`, `webhooks`) rather than by technical layer (`routers`, `services`). This enhances cohesion and makes the codebase easier to navigate and maintain.
*   **Clean Separation of Concerns**: Within each feature, code is separated into `controller.py` (Presentation), `service.py` (Application/Business Logic), and `models.py` (Data Contracts).
*   **Shared Domain**: Core database models (SQLAlchemy entities) are shared across features and reside in the `src/entities/` directory.

For a detailed explanation of the architecture, please see [architecture.md](./architecture.md).

## Features

*   **Room Management**: Create and configure video rooms with specific parameters (e.g., max participants).
*   **Token-Based Authentication**: Generate secure, short-lived JWT access tokens for clients to join LiveKit rooms.
*   **Webhook Handling**: Securely ingest, validate, and process real-time events from the LiveKit server (e.g., `participant_joined`, `room_finished`).
*   **Database Persistence**: Store room configurations in a PostgreSQL database using SQLAlchemy ORM.
*   **Database Migrations**: Manage database schema changes seamlessly with Alembic.
*   **Dockerized Environment**: Fully containerized for consistent development and deployment using Docker and Docker Compose.

## API Endpoints

The API is versioned under the `/v1` prefix. When the application is running, full interactive documentation is available at `http://localhost:8000/docs`.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/v1/rooms/` | Creates a new meeting room. |
| `POST` | `/v1/rooms/{room_name}/token` | Generates a join token for a user to enter a room. |
| `POST` | `/v1/livekit/webhook` | Receives and validates webhooks from the LiveKit server. |
| `GET` | `/v1/health` | A simple health check endpoint. |

---

## Prerequisites

Before you begin, ensure you have the following installed on your local machine:
*   [Docker](https://www.docker.com/get-started)
*   [Docker Compose](https://docs.docker.com/compose/install/) (usually included with Docker Desktop)

## Getting Started

Follow these steps to get the development environment up and running.

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Configure Environment Variables

Create a `.env` file by copying the example template.

```bash
cp .env.example .env
```

Now, open the `.env` file and fill in your specific credentials.

```dotenv
# .env

# The PostgreSQL connection details are used by both the app and docker-compose.
# The default values are set to work with the provided docker-compose.yml.
DATABASE_URL=postgresql://user:password@db:5432/qari_db

# --- REQUIRED: LiveKit Server Credentials ---
# Find these in your LiveKit Cloud project settings.
LIVEKIT_URL=wss://your-project-name.livekit.cloud
LIVEKIT_API_KEY=API...
LIVEKIT_API_SECRET=...

# A secret key for general application purposes.
APP_SECRET_KEY=a_very_secret_and_long_random_string_for_security
```

### 3. Build and Run with Docker Compose

This command will build the Docker images for the FastAPI application and the PostgreSQL database, create the containers, and start them.

```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`.

### 4. Apply Database Migrations

The first time you run the application, or any time the database schema changes (i.e., you modify a model in `src/entities/`), you need to apply the migrations.

Open a new terminal and run:

```bash
docker-compose exec app alembic upgrade head
```

This command executes Alembic inside the running `app` container and applies all migrations up to the latest version.

---

## Development Workflow

### Database Migrations with Alembic

When you make changes to your SQLAlchemy models in the `src/entities/` directory, you need to generate a new migration script.

1.  **Ensure your application container is running**: `docker-compose up`
2.  **Generate a new revision file**:

    ```bash
    docker-compose exec app alembic revision --autogenerate -m "A short description of the changes"
    ```
3.  **Apply the new migration**:
    ```bash
    docker-compose exec app alembic upgrade head
    ```

### Running Tests

The project includes a comprehensive test suite using `pytest`. The tests are separated into `unit` and `e2e` (end-to-end) tests.

To run all tests and view a coverage report, execute the following command:

```bash
docker-compose exec app pytest
```

This will run all files matching the `test_*.py` pattern inside the `tests/` directory within the running container.

## Project Structure

The project follows a feature-driven directory structure for scalability and maintainability.

```
.
├── alembic/              # Alembic migration scripts
├── src/                  # Main application source code
│   ├── main.py           # FastAPI application entry point
│   ├── api.py            # Aggregates all feature routers
│   ├── config.py         # Pydantic settings management
│   ├── exceptions.py     # Custom HTTP exceptions
│   │
│   ├── database/
│   │   └── core.py       # SQLAlchemy engine and session management
│   │
│   ├── entities/         # Shared SQLAlchemy ORM models (The "Domain")
│   │   └── room_entity.py
│   │
│   ├── features/
│   │   ├── rooms/        # "Rooms" feature slice
│   │   │   ├── controller.py
│   │   │   ├── service.py
│   │   │   └── models.py
│   │   └── webhooks/     # "Webhooks" feature slice
│   │       ├── controller.py
│   │       ├── service.py
│   │       └── models.py
│
└── tests/                # Application tests
    ├── e2e/              # End-to-end tests
    └── unit/             # Unit/Integration tests
```