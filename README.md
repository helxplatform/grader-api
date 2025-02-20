# EduHeLx Grader API
A microservice supporting student submissions to otter grader within EduHeLx



## Usage

### Installation
You'll need to have installed libpq (Postgres client) first before installing psycopg2 (Postgres driver).
```bash
# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Setup .env
cp .env.sample .env
vim .env
```

### Running
```bash
set -a && source .env
python -m app.main
# or
uvicorn --reload app.main:app --log-level=info
```

### Documentation
The OpenAPI UI is accessible under /docs. To login, first use the login endpoint to get access/refresh tokens.
Then, under Authorize (lock icon), set the value to `Bearer {access_token}`.

## Application Startup

Our application startup is handled by the `start.py` script. This script performs
different actions depending on whether it's running inside a Kubernetes cluster
or in a Docker container.

When running in Kubernetes, we assume that a ConfigMap and a Secret are mounted
at `/etc/grader-config` and `/etc/grader-secret` respectively. These contain the
non-sensitive and sensitive configuration parameters for our application.
The `start.py` script will combine the values from these two sources into a
single `.env` file at `/app/.env`, which is then used by our application for its
configuration.

When running in Docker, we expect the `.env` file to be provided directly.
The `start.py` script checks for the existence of this file and if it 
exists, it tries to load the environment variables using python-dotenv.

After the `.env` file has been created or checked, the `start.py` script starts
the application using the Uvicorn ASGI server.

## Password Secret Generator

The password secret generator is a Python script that generates a random
12-character alphanumeric password and creates a Kubernetes Secret with this
password. The name of the Secret is `grader-postgresql`.

Before creating the Secret, the script checks if a Secret with this name already
exists. If it does, the script prints a message and does not create a new Secret.
This prevents accidental overwriting of existing Secrets.

The generated password is used for the PostgreSQL database that our application
connects to. It's important to handle this password securely, as it provides
access to the database.

## Alembic Migrations with Environment Variable Based Configuration

This approach uses Alembic for database migrations in a Python project. Alembic
configurations are set based on environment variables, providing flexibility to
work across different environments.

## Configuration

The database connection URL is primarily configured through environment
variables. The `config.py` module in the project constructs the database URL
based on these environment variables.

If the necessary environment variables are not set, the configuration falls back
to the `sqlalchemy.url` specified in the `alembic.ini` file.

### Database Schema

<img src="/resources/DatabaseDesign.png" >

## Running Migrations

Before running the server, Alembic is invoked to migrate the database to the
most up-to-date revision (the "head"). The `start.py` script has been augmented
to include this step.

In the `env.py` file, the following code is used to set the database URL:

### Try to import config module and get the database URL

Attempt to get the configuration from the server config, but if that fails
use the default from the alembic config

    try:
         from app.core.config import settings
         config.set_main_option('sqlalchemy.url',settings.SQLALCHEMY_DATABASE_URI)
     except Exception:
         pass

### Now proceed with the rest of the env.py file...

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
