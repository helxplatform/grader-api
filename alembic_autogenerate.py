#!/usr/bin/env python

import os
import sys

from dotenv import load_dotenv

from alembic import command
from alembic.config import Config

# Load .env file if exists
if os.path.exists('.env'):
    load_dotenv('.env')

# Get the revision message from the command-line arguments
try:
    message = sys.argv[1]
except IndexError:
    print("Please provide a revision message as a command-line argument.")
    sys.exit(1)

# Load Alembic configuration
alembic_cfg = Config("alembic.ini")

# Generate a new migration file by comparing the current state of the database
# with the state of the SQLAlchemy models
command.revision(alembic_cfg, message, autogenerate=True)
