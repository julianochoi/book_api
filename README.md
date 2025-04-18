# Book API

## Configuration
- Create a copy of `.env.example` and name it `.env`.
- Update the `.env` file with your database connection details.
- Generate a secret key to secure the jwt tokens:
```bash
openssl rand -hex 32
```
- Update the `JWT_SECRET` variable in the `.env` file with the generated secret key.
- Update the `DATABASE_URL` variable in the `.env` file with your database connection string.
