# Py Online Cinema

Py Online Cinema is an online cinema backend developed with FastAPI. The project is designed as a REST API for an online cinema platform and is being developed using a feature-branch workflow.

## Technologies

Python 3.11, FastAPI, Uvicorn, SQLAlchemy, SQLite, aiosqlite, Pydantic, EmailStr, pwdlib, Argon2, Poetry, Docker, Docker Compose and pytest.

## Project Description

Py Online Cinema is a backend application for an online cinema service. The project is built with FastAPI and uses asynchronous SQLAlchemy with SQLite for database operations. The application provides API endpoints for user registration and is prepared for further cinema functionality such as movies, carts, orders and other features that will be implemented in separate feature branches.

The project follows a modular architecture where database models, Pydantic schemas, business logic and API routers are separated into different modules.

## Project Structure

py-online-cinema/
├── app/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── user_group.py
│   ├── routers/
│   │   └── auth.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── auth.py
│   ├── services/
│   │   └── auth.py
│   ├── database.py
│   ├── init_db.py
│   ├── main.py
│   └── seed.py
├── .dockerignore
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── poetry.lock
├── poetry.toml
├── pyproject.toml
└── README.md

## FastAPI Application

The main FastAPI application is located in app/main.py.

The application creates a FastAPI instance and includes the authentication router. The authentication router uses the /auth prefix.

The application is started with Uvicorn.

The default local address is:

http://localhost:8000

## Database

The project uses SQLite as the database.

SQLAlchemy is used as the ORM and aiosqlite is used as the asynchronous SQLite driver.

The database URL is:

sqlite+aiosqlite:///./cinema.db

The database configuration is located in app/database.py.

The project uses an asynchronous SQLAlchemy engine, AsyncSession, async_sessionmaker and a FastAPI database dependency.

The database file is cinema.db.

## Database Models

The project currently contains two database models: UserGroup and User.

### UserGroup Model

The UserGroup model represents user groups.

The model contains the following fields:

id - unique identifier of the group.

name - name of the group.

The database table is user_groups.

### User Model

The User model represents registered users.

The model contains the following fields:

id - unique identifier of the user.

email - user's email address. The field is unique.

hashed_password - securely hashed user password.

is_active - indicates whether the user is active. The default value is False.

created_at - date and time when the user was created.

updated_at - date and time when the user was updated.

group_id - foreign key referencing the user_groups table.

The database table is users.

## Database Initialization

The project contains app/init_db.py for database initialization.

The script creates all tables defined in SQLAlchemy metadata.

The database can be initialized with:

python -m app.init_db

During development the database structure was verified through SQLAlchemy metadata and the following tables were created:

user_groups

users

## Seed Data

The project contains app/seed.py.

The seed script creates the default user group named user.

The default user group is required when registering a new user.

Run the seed script with:

python -m app.seed

## Authentication

Authentication functionality is separated into three layers.

The API router is located in:

app/routers/auth.py

The Pydantic schemas are located in:

app/schemas/auth.py

The business logic is located in:

app/services/auth.py

This separation keeps the router responsible for HTTP requests while the service contains the registration logic.

## User Registration

The project currently provides a user registration endpoint.

Endpoint:

POST /auth/register

The endpoint accepts an email and password.

Example request:

{
  "email": "danilo@example.com",
  "password": "password123"
}

The email is validated with Pydantic EmailStr.

The password must contain at least 8 characters and no more than 128 characters.

Before creating a user, the application checks whether another user with the same email already exists.

If the email is already registered, the user is not created.

The registration endpoint searches for the default user group named user.

If the default user group is not available, the endpoint returns a server error because registration requires an existing user group.

After successful validation, the password is hashed and the new user is saved to the database.

The newly registered user is automatically assigned to the default user group.

The new user is initially inactive.

The endpoint returns HTTP status code 201 Created.

Example response:

{
  "id": 1,
  "email": "danilo@example.com",
  "is_active": false
}

## Password Security

Passwords are never stored as plain text.

The project uses pwdlib for password hashing and Argon2 as the recommended hashing algorithm.

The registration service creates a password hash before storing the user.

The database stores the hashed_password value instead of the original password.

## Pydantic Schemas

Authentication schemas are located in app/schemas/auth.py.

The RegisterRequest schema contains:

email

password

Email validation is performed with EmailStr.

Password validation requires a minimum of 8 characters and a maximum of 128 characters.

The RegisterResponse schema contains:

id

email

is_active

The response does not expose the user's password or password hash.

## Authentication Service

The registration business logic is implemented in app/services/auth.py.

The registration service performs the following operations:

1. Searches for an existing user with the requested email.
2. Prevents registration if the email already exists.
3. Hashes the user's password.
4. Creates a new User object.
5. Adds the new user to the database session.
6. Commits the database transaction.
7. Returns the created user.

## API Router

The authentication router is located in app/routers/auth.py.

The router uses the /auth prefix.

The registration endpoint is:

POST /auth/register

The endpoint uses RegisterRequest as the request schema and RegisterResponse as the response schema.

The database session is provided through the get_db FastAPI dependency.

The endpoint searches for the default user group and passes the group and registration data to the registration service.

## Swagger Documentation

FastAPI automatically generates API documentation.

Swagger UI is available at:

http://localhost:8000/docs

ReDoc is available at:

http://localhost:8000/redoc

The current API documentation contains:

POST /auth/register

The registration endpoint was tested successfully through Swagger UI.

## Poetry

The project uses Poetry for dependency management.

Project dependencies are defined in pyproject.toml.

The locked dependency versions are stored in poetry.lock.

Poetry was configured not to create a separate virtual environment for the project.

Dependencies can be installed with:

poetry install

The project uses Python 3.11.

## Local Development

Create a virtual environment:

python3.11 -m venv venv

Activate the virtual environment:

source venv/bin/activate

Install project dependencies:

poetry install

Initialize the database:

python -m app.init_db

Create the default user group:

python -m app.seed

Start the application:

uvicorn app.main:app --reload

The application will be available at:

http://localhost:8000

Swagger documentation will be available at:

http://localhost:8000/docs

## Environment Variables

The project supports environment variables through the .env file.

The .env file is excluded from Git and Docker using the appropriate ignore files.

Environment-specific configuration should be stored in .env rather than committed to the repository.

Example:

DATABASE_URL=sqlite+aiosqlite:///./cinema.db

Sensitive information should not be committed to the repository.

## Docker

The project was containerized using Docker.

Docker configuration consists of:

Dockerfile

.dockerignore

docker-compose.yml

## Dockerfile

The Dockerfile uses the Python 3.11 slim image:

python:3.11-slim

The Docker image performs the following steps:

1. Uses Python 3.11 slim as the base image.
2. Sets /app as the working directory.
3. Installs Poetry.
4. Copies pyproject.toml and poetry.lock.
5. Configures Poetry not to create a virtual environment.
6. Installs the main project dependencies.
7. Copies the app directory into the container.
8. Runs the FastAPI application using Uvicorn.

The container starts the application with:

uvicorn app.main:app --host 0.0.0.0 --port 8000

## Docker Ignore

The .dockerignore file excludes unnecessary files from the Docker build context.

It currently excludes:

venv/

.git/

.idea/

.pytest_cache/

__pycache__/

*.pyc

.env

cinema.db

tests/

This keeps the Docker build context smaller and prevents local environment files and development-only files from being copied into the image.

## Docker Compose

The application is configured in docker-compose.yml.

The service is named app.

The Docker image is built from the current project directory.

The container name is:

py-online-cinema

The application exposes port 8000.

The port mapping is:

8000:8000

The .env file is loaded using env_file.

The Docker Compose configuration is:

services:
  app:
    build: .
    container_name: py-online-cinema
    ports:
      - "8000:8000"
    env_file:
      - .env

## Running with Docker

Build the Docker image:

docker compose build

Start the application:

docker compose up

The application will be available at:

http://localhost:8000

Swagger documentation will be available at:

http://localhost:8000/docs

Stop the application:

docker compose down

## Docker Testing

The Docker image was successfully built with:

docker compose build

The build completed successfully and created the py-online-cinema-app image.

The application was successfully started with:

docker compose up

The Docker container was successfully exposed on port 8000.

The final Docker port mapping was:

0.0.0.0:8000->8000/tcp

The Swagger documentation was successfully opened through the Dockerized application.

The POST /auth/register endpoint was also successfully tested through Swagger.

During Docker testing, port 8000 was initially occupied by another Docker container named backend_theater. The existing container was stopped, after which the py-online-cinema container was successfully started on port 8000.

The container was later stopped correctly with:

docker compose down

## Testing

The project uses pytest for automated testing.

Run tests with:

pytest

Tests will be added and expanded as new project functionality is implemented.

## Git Workflow

The project uses a feature-branch workflow.

The main branches are:

main

develop

Feature branches are created from develop.

The project currently contains feature branches for separate functionality.

Registration was developed in:

feature/registration

Docker configuration was developed in:

feature/docker

The project follows the FLEX development approach of making small, logical commits after completing individual changes.

Each feature is developed separately and can later be merged into develop.

## Current Project Status

The project currently contains the basic FastAPI application and the first implemented functionality.

Completed functionality includes:

- Project initialization
- Git repository setup
- main branch
- develop branch
- Feature branch workflow
- feature/registration branch
- feature/docker branch
- Python 3.11 setup
- Poetry setup
- FastAPI setup
- Uvicorn setup
- SQLAlchemy setup
- aiosqlite setup
- SQLite database
- AsyncSession
- async_sessionmaker
- database dependency
- SQLAlchemy Declarative Base
- UserGroup model
- User model
- User database table
- UserGroup database table
- Database initialization script
- Default user group seed script
- Pydantic registration schemas
- Email validation
- Password validation
- Password hashing
- Argon2 password hashing
- User registration service
- User registration router
- Duplicate email checking
- Default user group assignment
- Swagger documentation
- ReDoc documentation
- Environment variable support
- Dockerfile
- .dockerignore
- Docker Compose
- Successful Docker image build
- Successful Docker container startup
- Successful Swagger testing inside Docker

## Current API Endpoints

The currently implemented API endpoint is:

POST /auth/register

The endpoint registers a new user, validates the input, hashes the password, assigns the default user group and saves the user to the SQLite database.

## Future Development

The project is still under active development.

Future functionality will be implemented in separate feature branches according to the project requirements.

The online cinema will be expanded with additional functionality such as cinema-related entities, movie management, cart functionality, orders and other required API endpoints.

## License

This project was created for educational purposes as part of the Python development course.
