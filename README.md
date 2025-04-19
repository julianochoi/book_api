# Book API
## Description
Book API is a RESTful API for managing books.

## Features
- Create, read, update(partial), and delete books.
- Pagination for book listing.
- User authentication and authorization using JWT.
- SSE (Server-Sent Events) for real-time updates on book events.
- Fully documented API using OpenAPI.
- Dockerized for easy deployment.

## Requirements
* [Docker](https://www.docker.com/)
* [Docker Compose](https://docs.docker.com/compose/install/)
* [Poetry](https://python-poetry.org/docs/#installation)
* [Python 3.13+](https://www.python.org/downloads/)

## Configuration
- Create a copy of `.env.example` and name it `.env`.
- Update the `.env` file with your database connection details.
- Generate a secret key to secure the jwt tokens:
```bash
openssl rand -hex 32
```
- Update the `JWT_SECRET` variable in the `.env` file with the generated secret key.
- Update the `DATABASE_URL` variable in the `.env` file with your database connection string.

## Deployment
1. Clone the repository:
```bash
git clone git@github.com:julianochoi/book_api.git
cd book_api
```
1. Setup environment variables according to [Configuration](#configuration).
1. Deploy the application using Docker Compose:
```bash
docker-compose up -d
```

## Usage
1. Access the API documentation at `http://localhost:8000/docs`.
1. Use the `/auth/register` endpoint to create a new user.
1. Use the `/auth/login` endpoint to authenticate and receive a JWT token.
1. Use the JWT token to access the CRUD endpoints for books.
- Use the `/books` endpoints to create, read, update, and delete books.
- Use the `sse/updates/books` endpoint to receive real-time updates on book events.

## Testing
There are multiple ways to run the tests depending on your environment:

### Dev Containers
1. Open the project in VSCode.
1. Open the command palette (Ctrl+Shift+P) and select "Remote-Containers: Reopen in Container".
1. Wait for the container to build and start.
1. Open the terminal in VSCode and make sure the virtual environment is activated.
1. Run the tests using:
	```bash
	make test
	```

### Docker Compose
1. Build and run the application using Docker Compose:
	```bash
	docker compose up -d --build
	```
1. Install the test dependencies:
	```bash
	docker compose exec app make install
	```
1. Run the tests using:
	```bash
	docker compose exec app make test
	```

### Local Environment
1. Create a virtual environment:
	```bash
	python -m venv .venv
	source venv/bin/activate
	```
1. Install the dependencies:
	```bash
	make install
	```
1. Run the tests using:
	```bash
	make test
	```