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
